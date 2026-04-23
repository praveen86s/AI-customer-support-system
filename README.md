# 🤖 AI Customer Support System

An **Agentic AI-powered Customer Support Assistant** built using **Streamlit**, **Google Gemini**, and **FastMCP**.

This project automates **customer return and refund workflows** by allowing users to chat with an AI support bot that can:

* Retrieve order details
* Check return eligibility
* Process refunds automatically

It demonstrates how **Agentic AI + tool calling** can automate repetitive customer service operations.

---

## 🚀 Features

* 💬 **Interactive Chat Interface** using Streamlit
* 🧠 **Autonomous Decision Making** using Gemini
* 🛠 **Tool Calling with FastMCP**
* 📦 **Order Lookup Tool**
* 📄 **Return Policy Verification Tool**
* 💰 **Refund Processing Tool**

---

## 🏗 Project Architecture

The AI agent follows an **Agent → Tool → Response** workflow:

1. User submits a customer support request
2. Gemini analyzes the request
3. Calls the required tool:

   * `get_order_details()`
   * `check_return_policy()`
   * `issue_refund()`
4. Tool response is passed back to Gemini
5. Final customer support response is generated

---

## 📂 Project Structure

```bash
AI-customer-support-system/
│── app.py
│── requirements.txt
│── .gitignore
│── README.md
│── .env   # local only, ignored in git
```

---

## ⚙ Technologies Used

* **Python**
* **Streamlit**
* **Google Gemini API**
* **FastMCP**
* **JSON**
* **Environment Variables**

---

## 🧪 Mock Database

The project uses a sample order database:

```python
DATABASE = {
    "ORD-123": {
        "item": "Laptop",
        "price": 1200.00,
        "status": "delivered",
        "days_since_purchase": 14
    },
    "ORD-456": {
        "item": "Headphones",
        "price": 150.00,
        "status": "delivered",
        "days_since_purchase": 45
    }
}
```

---

## 🔑 Environment Variables

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_google_gemini_api_key
```

---

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/your-username/AI-customer-support-system.git
cd AI-customer-support-system
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
streamlit run app.py
```

---

## 💡 Example Prompts

### Eligible Refund

> Hi, my order is ORD-123. The screen is glitchy. Can I get a refund?

### Ineligible Refund

> Hello, I bought headphones on order ORD-456. Please refund.

---

## 📈 Business Value

This project helps businesses by:

* Reducing manual support workload
* Improving customer response times
* Automating repetitive refund operations
* Enhancing customer satisfaction
* Lowering operational costs

---

## 🔄 Scalability

This system can be scaled by integrating with:

* Real order databases
* Payment gateways
* CRM systems
* Order tracking APIs
* Cloud deployment infrastructure
* Multi-language customer support

Future improvements:

* Support ticket escalation
* Analytics dashboard
* Customer sentiment analysis
* Voice support integration

---

## 🎯 Use Cases

* E-commerce customer support
* Refund automation
* Return management systems
* Order tracking assistants
* AI-powered helpdesks

---


## 📌 Conclusion

This project demonstrates how **Agentic AI systems** can autonomously perform customer support operations by reasoning over customer requests and invoking tools dynamically.

It is a practical example of combining:

* **LLMs**
* **Tool Calling**
* **Autonomous Agents**
* **Business Workflow Automation**

to create **intelligent customer support systems**.

---

## 👨‍💻 Author

Developed as an **Agentic AI automation project** using **Gemini + FastMCP + Streamlit**
