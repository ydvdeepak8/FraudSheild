// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

contract Payments {
    struct Payment {
        address sender;
        address receiver;
        uint amount;
        uint timestamp;
    }

    Payment[] public transactions;
    event PaymentSent(address indexed from, address indexed to, uint amount);

    function sendPayment(address payable _receiver) public payable {
        require(msg.value > 0, "Send some ETH");

        transactions.push(Payment(msg.sender, _receiver, msg.value, block.timestamp));
        _receiver.transfer(msg.value);

        emit PaymentSent(msg.sender, _receiver, msg.value);
    }

    function getPayments() public view returns (Payment[] memory) {
        return transactions;
    }
 
function getBalance() public view returns (uint) {
    return address(this).balance;
}

}
