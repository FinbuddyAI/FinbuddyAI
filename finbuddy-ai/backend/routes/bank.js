const express = require('express');
const router = express.Router();
const { BankAccount, Transaction } = require('../models/bankAccount');
const { generateMockBankData } = require('../services/mockBankData');
const auth = require('../middleware/auth');

// Initialize bank data for a new user
router.post('/init', auth, async (req, res) => {
  try {
    // Check if user already has bank data
    const existingAccount = await BankAccount.findOne({ user: req.user.id });
    if (existingAccount) {
      return res.status(400).json({ message: 'Bank data already initialized' });
    }

    // Generate mock data
    const mockData = generateMockBankData(req.user.id);

    // Save account
    const account = new BankAccount(mockData.accounts[0]);
    await account.save();

    // Save transactions
    const transactions = mockData.transactions.map(tx => new Transaction(tx));
    await Transaction.insertMany(transactions);

    res.json({ message: 'Bank data initialized successfully' });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Get bank account data
router.get('/data', auth, async (req, res) => {
  try {
    const account = await BankAccount.findOne({ user: req.user.id });
    if (!account) {
      return res.status(404).json({ message: 'No bank account found' });
    }

    const transactions = await Transaction.find({ account_id: account.account_id })
      .sort({ date: -1 });

    res.json({
      accounts: [account],
      transactions: transactions
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Server error' });
  }
});

module.exports = router; 