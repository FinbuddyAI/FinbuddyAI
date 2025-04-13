const express = require('express');
const router = express.Router();
const { BankAccount, Transaction } = require('../models/bankAccount');
const { generateMockAccount, generateMockTransactions } = require('../services/mockBankData');
const auth = require('../middleware/auth');

// Link bank account (generate mock data)
router.post('/link', auth, async (req, res) => {
  try {
    // First, check if user already has a bank account
    const existingAccount = await BankAccount.findOne({ user: req.user.id });
    if (existingAccount) {
      return res.status(400).json({ message: 'Bank account already linked' });
    }

    // Generate mock account
    const mockAccount = generateMockAccount(req.user.id);
    const account = await BankAccount.create(mockAccount);

    // Generate mock transactions for the last 2 months
    const endDate = new Date();
    const startDate = new Date();
    startDate.setMonth(startDate.getMonth() - 2);
    
    const mockTransactions = generateMockTransactions(account.account_id, startDate, endDate);
    await Transaction.insertMany(mockTransactions);

    res.status(201).json({ message: 'Bank account linked successfully' });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Disconnect bank account
router.delete('/disconnect', auth, async (req, res) => {
  try {
    const account = await BankAccount.findOne({ user: req.user.id });
    if (!account) {
      return res.status(404).json({ message: 'No bank account found' });
    }

    // Delete all transactions for this account
    await Transaction.deleteMany({ account_id: account.account_id });
    // Delete the account
    await account.remove();

    res.json({ message: 'Bank account disconnected successfully' });
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
      account: {
        account_id: account.account_id,
        name: account.name,
        mask: account.mask,
        balances: account.balances
      },
      transactions
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Server error' });
  }
});

module.exports = router; 