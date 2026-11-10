# expense-tracker-ai 

A web application built with Python and Django that automatically extracts, structures, and categorizes itemized data from receipt images using the OpenAI API.

## How It Works
1. **Upload:** User uploads a receipt image through the Django web interface.
2. **AI Processing:** The image is sent to the OpenAI API, which extracts item names, quantities, prices, and totals.
3. **Database & Admin:** Processed data is saved into the database, allowing full management and adjustments via Django Admin.
4. **Structured Display:** The parsed information is cleanly presented to the user in structured tables with automated categorization and sum validation.

## Tech Stack
* **Backend:** Python, Django
* **AI Integration:** OpenAI API
* **Database:** SQLite (managed via Django ORM)
* **Frontend:** HTML, Bootstrap

## Screenshots
<img width="949" height="602" alt="Screenshot 2026-10-12 at 22 29 18" src="https://github.com/user-attachments/assets/04532615-714f-4632-894d-952cf9b3c17a" />

## Roadmap / Future Improvements
* [ ] Add user authentication (login/register).
* [ ] Implement monthly expense analytics and charts.
* [ ] Export data to Excel/CSV.
