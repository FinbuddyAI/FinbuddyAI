const { v4: uuidv4 } = require('uuid');

const categories = ['Food', 'Transportation', 'Travel', 'Shopping', 'Rent', 'Other'];
const merchants = {
  Food: ['Starbucks', 'McDonalds', 'Whole Foods', 'Local Restaurant', 'Pizza Place'],
  Transportation: ['Uber', 'Lyft', 'Gas Station', 'Public Transit'],
  Travel: ['Airbnb', 'Hotel', 'Airline'],
  Shopping: ['Amazon', 'Target', 'Walmart', 'Best Buy'],
  Rent: ['Apartment Rent'],
  Other: ['Netflix', 'Spotify', 'Gym Membership']
};

function generateMockAccount(userId) {
  return {
    account_id: `acct_${uuidv4()}`,
    name: 'Primary Checking',
    mask: Math.floor(Math.random() * 9000) + 1000,
    balances: {
      available: 1500.00,
      current: 1500.00,
      iso_currency_code: 'USD'
    },
    user: userId
  };
}

function generateMockTransactions(accountId, numDays = 60) {
  const transactions = [];
  const today = new Date();
  
  for (let i = 0; i < numDays; i++) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    
    // Generate 0-3 transactions per day
    const numTransactions = Math.floor(Math.random() * 4);
    
    for (let j = 0; j < numTransactions; j++) {
      const category = categories[Math.floor(Math.random() * categories.length)];
      const merchant = merchants[category][Math.floor(Math.random() * merchants[category].length)];
      const amount = category === 'Rent' 
        ? -1200.00 
        : category === 'Income'
          ? 2000.00
          : (Math.random() * 200 - 100).toFixed(2);
      
      transactions.push({
        transaction_id: `tx_${uuidv4()}`,
        account_id: accountId,
        date: date.toISOString().split('T')[0],
        amount: parseFloat(amount),
        name: merchant,
        category: category
      });
    }
  }
  
  return transactions;
}

function generateMockBankData(userId) {
  const account = generateMockAccount(userId);
  const transactions = generateMockTransactions(account.account_id);
  
  return {
    accounts: [account],
    transactions: transactions
  };
}

module.exports = {
  generateMockBankData
}; 