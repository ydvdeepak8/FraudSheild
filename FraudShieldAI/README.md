🔥 Blockchain Fraud Detection and ETH Transaction System

This project provides a Fraud Detection System combined with Ethereum (ETH) Transactions, with authentication powered by Firebase.It uses Hardhat for deploying smart contracts, and machine learning for detecting frauds before transactions.

🧹 Flow Overview

(Replace path/to/your/image.jpg with your actual image path.)

Flow Summary:

User can Login or Sign Up.

Authentication handled with Firebase.

After login:

Landing Page → Choose between Fraud Detection or Send ETH.

If sending ETH, the system:

Predicts fraud possibility.

If fraud detected ➔ Sends alert email.

If no fraud ➔ Completes the transaction successfully.

📦 Tech Stack

Frontend: React.js / HTML-CSS (optional)

Backend: Node.js

Blockchain: Hardhat + Ethereum

Authentication: Firebase

Machine Learning: Fraud Detection Model

Email Notifications: SMTP / Nodemailer

🚀 How to Run the Project

1. Clone the Repository

git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

2. Install Dependencies

npm install

3. Set up Firebase

Create a project on Firebase Console.

Enable Authentication (Email/Password).

Copy the Firebase config and add it to your frontend/backend.

4. Run Local Ethereum Node (Hardhat Node)

npx hardhat node

5. Deploy Smart Contract

npx hardhat compile
npx hardhat run scripts/deploy.js --network localhost

(Or if using Hardhat Ignition module:)

npx hardhat ignition deploy ./ignition/modules/Lock.js

6. Start the Backend Server

npm run server

7. Start the Frontend

npm start

📜 Available Scripts

Inside the project directory, you can run:

Script

Purpose

npx hardhat help

See all available Hardhat commands.

npx hardhat test

Run smart contract tests.

npx hardhat node

Run a local Ethereum node.

npx hardhat ignition deploy ./ignition/modules/Lock.js

Deploy smart contract using Ignition module.

📧 Mail Alerts

If fraud is predicted by the model, an automatic email will be sent to the admin/user about the suspicious activity.

✨ Future Improvements

Deploy smart contracts to public testnets (Goerli, Sepolia).

Improve fraud detection model accuracy.

Add SMS alerts for detected frauds.

🤝 Contributing

Contributions, issues, and feature requests are welcome!Feel free to fork the repo and make a pull request.

🛡️ License

This project is licensed under the MIT License.