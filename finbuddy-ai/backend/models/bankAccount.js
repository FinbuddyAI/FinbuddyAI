const mongoose = require('mongoose');

const transactionSchema = new mongoose.Schema({
  transaction_id: { type: String, required: true },
  account_id: { type: String, required: true },
  date: { type: Date, required: true },
  amount: { type: Number, required: true },
  name: { type: String, required: true },
  category: { type: String, required: true }
});

const accountSchema = new mongoose.Schema({
  account_id: { type: String, required: true },
  name: { type: String, required: true },
  mask: { type: String, required: true },
  balances: {
    available: { type: Number, required: true },
    current: { type: Number, required: true },
    iso_currency_code: { type: String, required: true }
  },
  user: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true }
});

const Transaction = mongoose.model('Transaction', transactionSchema);
const BankAccount = mongoose.model('BankAccount', accountSchema);

module.exports = { BankAccount, Transaction }; 