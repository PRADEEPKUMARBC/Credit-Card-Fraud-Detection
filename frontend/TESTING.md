# Frontend Manual Test Plan

Run both servers first:
- Backend: `uvicorn backend.main:app --reload --port 8000`
- Frontend: `npm run dev` (inside `frontend/`)

Open: http://localhost:5173/

---

## 1. Header

- [ ] FraudGuard logo shows on the left
- [ ] Nav shows Dashboard, Predict, Performance, About
- [ ] The active page's nav item has a blue-tinted background
- [ ] A small green dot + "API Online" appears on the right
- [ ] On mobile (< 640px), labels hide and only icons show

## 2. Dashboard

- [ ] Four stat cards show: Total Transactions, Fraud Cases, Genuine Cases, Fraud Percentage
- [ ] Total = 283,726 (numbers format with commas)
- [ ] Fraud = 473, Genuine = 283,253, Fraud % = 0.1667
- [ ] Model Performance panel shows bars for Precision, Recall, F1, ROC-AUC
- [ ] All four metric bars are more than half filled
- [ ] Class Distribution chart shows two bars — one very tall, one almost invisible
- [ ] Refresh button re-fetches data (loading skeletons appear briefly)
- [ ] Quick Start card lists four steps

## 3. Predict

- [ ] Header shows a blue shield icon, title, and description
- [ ] Form has 30 input fields (Time, V1..V28, Amount)
- [ ] Toolbar has three buttons: Load Fraud Example, Load Genuine Example, Reset
- [ ] Click **Load Fraud Example**:
  - [ ] All 30 fields fill with numeric values
- [ ] Click **Predict Transaction**:
  - [ ] "Predicting…" appears on the button
  - [ ] A red toast slides in: "Fraud detected · 98.xx% confidence"
  - [ ] Result card appears with red header "Fraudulent Transaction"
  - [ ] Probability bar is nearly full and red
  - [ ] Risk Level badge says "High"
- [ ] Click **Load Genuine Example** → **Predict Transaction**:
  - [ ] Green toast appears
  - [ ] Result card shows "Genuine Transaction" with Low risk
- [ ] Click **Reset**:
  - [ ] All fields become "0"
- [ ] Clear any field (e.g., Amount) → click **Predict**:
  - [ ] Red "Required" error under that field
  - [ ] No request is sent (Network tab stays quiet)
- [ ] Stop the backend (Ctrl+C in the Uvicorn terminal):
  - [ ] Click Predict → red toast "No response from server…"
  - [ ] Green dot in header turns red within ~20 s
- [ ] Restart the backend → header dot turns green within ~20 s

## 4. Performance

- [ ] Four metric cards appear (Precision, Recall, F1, ROC-AUC)
- [ ] Values match the ones from the backend `/metrics` endpoint
- [ ] Confusion Matrix grid shows four colored cells
  - [ ] Top-left (TN): green
  - [ ] Top-right (FP): yellow
  - [ ] Bottom-left (FN): red
  - [ ] Bottom-right (TP): blue
- [ ] Four report images load and display
- [ ] Hovering a report image card doesn't distort the layout
- [ ] Refresh button works

## 5. About

- [ ] Project title and description render
- [ ] Dataset section explains the 284,807 transactions and 492 frauds
- [ ] Pipeline section lists 11 steps
- [ ] Tech stack grid has three columns on desktop, one on mobile

## 6. Routing

- [ ] Clicking nav items changes the URL (/, /predict, /performance, /about)
- [ ] Manual URL to /xyz shows the 404 page with a "Back to Dashboard" button
- [ ] Back/forward browser buttons work correctly
- [ ] On every route change, content fades in

## 7. Accessibility & UX

- [ ] Tab through nav links — visible focus rings appear
- [ ] Tab through form fields — focus rings appear
- [ ] Tab to Predict button and press Enter — submits the form
- [ ] Toast announcements are aria-live (screen reader reads them)
- [ ] Reduced motion (system setting) disables the page transition and pulse dot
- [ ] Ctrl+P print preview hides header, footer, and buttons

## 8. Responsive layout

- [ ] At 1200px width: two-column layout on Dashboard
- [ ] At 800px width: columns stack, stat cards stack to 2-wide
- [ ] At 500px width: single column, form fields stack
- [ ] On all widths, no horizontal scrollbar appears

## 9. Console health

Open DevTools (F12) → Console.

- [ ] No red errors appear on any page
- [ ] No warnings about missing keys in lists
- [ ] Network tab shows only successful requests (200, 304)
- [ ] The proxy shows requests going to `/api/...`

---

## What to do if a test fails

1. Check the backend terminal for errors.
2. Check the browser console for errors.
3. Verify the backend is running (`curl http://127.0.0.1:8000/` should return JSON).
4. Try a hard refresh: Ctrl+Shift+R.
5. Restart Vite: Ctrl+C in the frontend terminal, then `npm run dev`.
6. If a metric looks wrong, run `python src/test_pipeline.py` to confirm the model is fine.