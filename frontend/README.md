# Frontend Client

The user interface for the Passport Management platform. It provides a clean, responsive, and real-time dashboard for users and administrators.

# Frontend Client

The user interface for the Passport Management platform. It provides a clean, responsive, and real-time dashboard for both ordinary users and administrators.

## Core Features
- **React 18 & Vite:** Fast build tooling and optimized rendering.
- **Real-Time Job Monitoring:** Listens to backend Server-Sent Events (SSE) to display live progress bars for document OCR extraction.
- **Drag-and-Drop Uploads:** Seamless document uploading interface.
- **Role-Based Dashboards:** Ordinary users can manage their own passports and uploads, while Administrators get extended tools to manage all users, distribute credits, and export system-wide data to CSV.

## Local Setup
1. Navigate to the directory: `cd frontend`
2. Install dependencies: `npm install`
3. Configure the environment variable for the API: `VITE_API_URL=http://localhost:8000`
4. Start the development server: `npm run dev`