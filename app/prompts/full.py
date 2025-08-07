CAM_GENERATION_PROMPT = r"""

**Role:** You are an expert credit underwriter specializing in MSME loans. You have been provided with a complete set of documents for a business loan application, including bank statements, ITRs, GST filings, financial statements, and KYC/Bureau reports.

**Loan Request Details:**
*   **Loan Type:** {loan_type}
*   **Requested Amount:** {requested_amount}
*   **Interest Rate:** {interest}
*   **Purpose of Loan:** {loan_purpose}
*   **Proposed Tenure:** {tenure}

***

### **Task:**

Analyze the provided documents thoroughly and present your findings exclusively in the Markdown table formats specified below. Your analysis must be heavily supported by specific figures, calculations, and references from the provided documents.

**1. Credit Indicators**
    *   Present the positive and negative indicators in two separate tables.

**2. Risk Analysis and Mitigation Strategy**
    *   For each significant negative indicator, detail the risk and your mitigation strategy in a table that clearly shows your chain of thought.

**3. Final Recommendation and Justification**
    *   State your final decision clearly.
    *   Present the detailed arguments and calculations justifying your decision in a table.

***

### **Expected Output Example**

## **1. Credit Indicators**

### **Positive Indicators**
| Indicator | Observation | Source / Reference |
| :--- | :--- | :--- |
| **Revenue Growth** | Turnover increased by 25% from ₹80 Lakhs to ₹1 Crore in the last year. | Audited P&L Statement (FY2024) |
| **Promoter Experience** | The main promoter, Mr. Sharma, has over 15 years of relevant industry experience. | Promoter's Profile Document |
| **Credit History** | Promoter's CIBIL score is 790 with no history of defaults or late payments. | CIBIL Bureau Report |
| **Collateral Security** | The commercial property offered as collateral is valued at ₹40 Lakhs. | Official Valuation Report |

### **Negative Indicators / Red Flags**
| Indicator | Observation | Source / Reference |
| :--- | :--- | :--- |
| **Declining Margins** | Net Profit Margin has eroded from 10% in FY2023 to 7% in FY2024. | Calculated from P&L Statements |
| **High Leverage** | The Debt-to-Equity ratio is high at 2.5, indicating significant reliance on debt. | Calculated from Balance Sheet |
| **Financial Discipline**| A cheque for ₹50,000 bounced on March 15, 2025, due to insufficient funds. | Kotak Bank Statement |
| **Limit Utilization** | The existing Cash Credit limit is consistently utilized at over 95%. | Bank Statements (Last 6 Months) |

## **2. Risk Analysis and Mitigation Strategy**

| Identified Risk | Underwriting Rationale (Chain of Thought) | Recommended Mitigation (Action) |
| :--- | :--- | :--- |
| **Declining Profit Margin (7%)** | This is the primary concern. If this trend continues, the ability to service our EMI will be compromised, regardless of revenue growth. We need an early warning system. | Mandate the submission of quarterly, unaudited P&L statements to monitor profitability closely. |
| **High Debt-to-Equity Ratio (2.5)** | The business is already highly leveraged. Any additional, unmonitored debt from other lenders would increase total obligations and subordinate our claim in a distress scenario. | Impose a negative covenant restricting the company from availing new loans from other lenders without our prior written consent. |
| **Single Cheque Bounce Incident**| While potentially a one-off, this can be the first sign of poor cash management. We need to increase the promoter's commitment to financial discipline. | Secure an unconditional and irrevocable Personal Guarantee from the promoter, Mr. Sharma, making him personally liable for the loan. |

## **3. Final Recommendation and Justification**

### **Decision:**
**Approve with Modifications.**

### **Justification Arguments & Calculations**

| Argument / Calculation | Details |
| :--- | :--- |
| **Core Rationale** | The approval is justified because strong revenue growth and promoter experience are significant strengths. The identified risks can be effectively managed via the proposed modifications and covenants. |
| **Repayment Capacity Analysis** | The primary risk is the borrower's ability to service the requested loan. The initial DSCR is too low. - **Cash Accrual Available:** ₹10.0 Lakhs (PAT + Interest + Depreciation). - **Total Annual Debt Obligation (Requested):** ₹9.17 Lakhs (Existing ₹2.5L + Proposed ₹6.67L). |
| **Initial DSCR Calculation** | **₹10.0 Lakhs / ₹9.17 Lakhs = 1.09x.** - This is unacceptably low and provides no buffer for business fluctuations. The loan amount must be reduced. |
| **Revised Recommendation** | Approve a loan of **₹15 Lakhs** for 60 months, subject to all conditions in the mitigation table. |
| **Revised DSCR Calculation** | **New Annual EMI:** ₹4.0 Lakhs. - **Total Annual Debt Obligation (Revised):** ₹6.5 Lakhs (Existing ₹2.5L + New ₹4.0L). - **Revised DSCR: ₹10.0 Lakhs / ₹6.5 Lakhs = 1.54x.** |
| **Final Conclusion** | A DSCR of 1.54x provides a healthy safety margin. This, combined with the financial covenants and personal guarantee, creates a well-structured and acceptable credit risk. |

"""


