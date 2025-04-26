const { ethers } = require("hardhat");

async function main() {
    const [signer] = await ethers.getSigners();
    const contractAddress = "0x5FbDB2315678afecb367f032d93F642f64180aa3"; // Your contract address

    const payments = await ethers.getContractAt("Payments", contractAddress, signer);

    const balance = await ethers.provider.getBalance(contractAddress);
    console.log("Contract Balance:", ethers.formatEther(balance), "ETH");  // Ethers v6 uses `formatEther` directly
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});
