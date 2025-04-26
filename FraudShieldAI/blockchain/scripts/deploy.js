const hre = require("hardhat");

async function main() {
    const Payments = await hre.ethers.getContractFactory("Payments");  // ✅ Fixed ethers import
    const payments = await Payments.deploy(); // Deploy the contract

    await payments.waitForDeployment();  // ✅ Updated for Hardhat 2.17.0+

    console.log("Contract deployed at:", await payments.getAddress());  // ✅ Updated for Hardhat 2.17+
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
