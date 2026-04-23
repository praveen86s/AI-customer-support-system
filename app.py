import streamlit as st
import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from fastmcp import FastMCP

# Load environment variables from the .env file
load_dotenv()

# ==========================================
# 1. DEFINE BUSINESS TOOLS & MCP SERVER
# ==========================================
mcp = FastMCP("CustomerSupportBot")

# Mock Database
DATABASE = {
    # 🟢 Standard Eligible Returns (< 30 days, delivered)
    "ORD-123": {"item": "Laptop", "price": 1200.00, "status": "delivered", "days_since_purchase": 14},
    "ORD-101": {"item": "Wireless Mouse", "price": 25.50, "status": "delivered", "days_since_purchase": 5},
    "ORD-108": {"item": "Smart Watch", "price": 250.00, "status": "delivered", "days_since_purchase": 21},
    
    # 🟡 Edge Cases (Exactly 30 days vs 31 days)
    "ORD-103": {"item": "Mechanical Keyboard", "price": 120.00, "status": "delivered", "days_since_purchase": 30},
    "ORD-104": {"item": "Office Chair", "price": 200.00, "status": "delivered", "days_since_purchase": 31},
    
    # 🔴 Ineligible Returns (> 30 days)
    "ORD-456": {"item": "Headphones", "price": 150.00, "status": "delivered", "days_since_purchase": 45},
    "ORD-105": {"item": "Smartphone", "price": 899.99, "status": "delivered", "days_since_purchase": 60},
    "ORD-109": {"item": "Desk Lamp", "price": 45.00, "status": "delivered", "days_since_purchase": 120},

    # 🔵 Complex States (Not delivered yet, or already returned)
    "ORD-102": {"item": "Gaming Monitor", "price": 350.00, "status": "in_transit", "days_since_purchase": 3},
    "ORD-106": {"item": "USB-C Hub", "price": 42.99, "status": "processing", "days_since_purchase": 1},
    "ORD-107": {"item": "Coffee Maker", "price": 85.00, "status": "already_refunded", "days_since_purchase": 15},
}

@mcp.tool()
def get_order_details(order_id: str) -> str:
    """Retrieves order details from the database using the order ID."""
    order = DATABASE.get(order_id.upper())
    if order:
        return json.dumps(order)
    return json.dumps({"error": "Order not found. Ask the user to verify the Order ID."})

@mcp.tool()
def check_return_policy(days_since_purchase: int) -> str:
    """Checks if an item is eligible for return based on days since purchase."""
    if days_since_purchase <= 30:
        return json.dumps({"eligible": True, "reason": "Within 30-day return window."})
    return json.dumps({"eligible": False, "reason": "Outside the 30-day return window. No refund allowed."})

@mcp.tool()
def issue_refund(order_id: str, amount: float) -> str:
    """Issues a refund to the customer's original payment method."""
    return json.dumps({
        "status": "SUCCESS", 
        "refunded_amount": amount, 
        "transaction_id": f"TXN-{order_id}-REFUND"
    })

TOOL_FUNCTIONS = [get_order_details, check_return_policy, issue_refund]


# ==========================================
# 2. STREAMLIT UI SETUP
# ==========================================
st.set_page_config(page_title="Agentic AI Support", page_icon="🤖", layout="centered")

st.title("🤖 Agentic Customer Support")


# Sidebar for config and reference
with st.sidebar:
    st.header("Configuration")
    # This will now automatically pull the value from the .env file
    api_key = st.text_input(
        "Gemini API Key", 
        type="password", 
        value=os.getenv("GEMINI_API_KEY", "")
    )
    
    st.divider()
    st.subheader("📦 Mock Database Reference")
    st.json(DATABASE)
    st.markdown("""
    **Try these prompts:**
    - *"Hi, my order is ORD-123. The screen is glitchy. Can I get a refund?"* (Valid)
    - *"Hello, I bought headphones on order ORD-456. Please refund."* (Invalid)
    """)

if not api_key:
    st.warning("Please add your Gemini API Key to the .env file or enter it in the sidebar.")
    st.stop()

# Initialize GenAI Client
client = genai.Client(api_key=api_key)


# ==========================================
# 3. STATE MANAGEMENT
# ==========================================
# We need two histories: 
# 1. API History (Complex GenAI objects for the model)
# 2. UI History (Simple dictionaries to render the chat)
if "api_history" not in st.session_state:
    st.session_state.api_history = []
if "ui_history" not in st.session_state:
    st.session_state.ui_history = []


# Render previous messages in the UI
for msg in st.session_state.ui_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ==========================================
# 4. AGENTIC CHAT LOOP
# ==========================================
if user_prompt := st.chat_input("How can I help you today?"):
    
    # 1. Display User Message & Save to State
    st.session_state.ui_history.append({"role": "user", "content": user_prompt})
    st.session_state.api_history.append(
        types.Content(role="user", parts=[types.Part.from_text(text=user_prompt)])
    )
    
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # 2. Start Agent Assistant Logic
    with st.chat_message("assistant"):
        
        # Use st.status to show the internal Agentic reasoning live!
        status = st.status("Agent is thinking...", expanded=True)
        
        # --- THE FROM-SCRATCH ReAct LOOP ---
        while True:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=st.session_state.api_history,
                config=types.GenerateContentConfig(
                    tools=TOOL_FUNCTIONS,
                    temperature=0.0,
                    system_instruction=(
                        "You are an autonomous Customer Support Agent. "
                        "Your goal is to help users with returns and refunds. "
                        "You must look up their order, check the return policy, and issue a refund if eligible. "
                        "Do not make up data. Always use the provided tools."
                    )
                )
            )

            # Append Agent's raw response to API history
            if response.candidates and response.candidates[0].content:
                st.session_state.api_history.append(response.candidates[0].content)

                # Show the Agent's internal thoughts in the UI status box
                for part in response.candidates[0].content.parts:
                    if part.text:
                        status.write(f"💭 **Thought:** {part.text.strip()}")

            # Check if Agent decided to take an Action (Call a Tool)
            if response.function_calls:
                for function_call in response.function_calls:
                    tool_name = function_call.name
                    tool_args = function_call.args 

                    status.write(f"🛠️ **Action:** Calling `{tool_name}` with args: `{tool_args}`")

                    # Find and execute the Python function dynamically
                    func_to_call = next((f for f in TOOL_FUNCTIONS if f.__name__ == tool_name), None)
                    
                    if func_to_call:
                        try:
                            tool_result = func_to_call(**tool_args)
                        except Exception as e:
                            tool_result = json.dumps({"error": str(e)})

                        status.write(f"✅ **Result:** `{tool_result}`")

                        # Pass the result back into the API history
                        st.session_state.api_history.append(
                            types.Content(
                                role="user",
                                parts=[
                                    types.Part.from_function_response(
                                        name=tool_name,
                                        response={"result": tool_result}
                                    )
                                ]
                            )
                        )
                    else:
                        status.write(f"❌ **Error:** Tool `{tool_name}` not found.")
                        break # Break out of loop if tool fails
            else:
                # No function calls = Agent is finished reasoning and acting!
                final_response = response.text
                status.update(label="Task Complete!", state="complete", expanded=False)
                
                # Display final response in UI and save to UI history
                st.markdown(final_response)
                st.session_state.ui_history.append({"role": "assistant", "content": final_response})
                break