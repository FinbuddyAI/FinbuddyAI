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

function generateMockTransactions(accountId, startDate, endDate) {
  const transactions = [];
  const days = Math.floor((endDate - startDate) / (1000 * 60 * 60 * 24));
  
  // Generate 2-4 transactions per day
  for (let i = 0; i < days; i++) {
    const currentDate = new Date(startDate);
    currentDate.setDate(currentDate.getDate() + i);
    
    const numTransactions = Math.floor(Math.random() * 3) + 2;
    for (let j = 0; j < numTransactions; j++) {
      const category = categories[Math.floor(Math.random() * categories.length)];
      const merchant = merchants[category][Math.floor(Math.random() * merchants[category].length)];
      
      // Generate reasonable amounts based on category
      let amount;
      switch(category) {
        case 'Rent':
          amount = -1200 + (Math.random() * 200 - 100);
          break;
        case 'Food':
          amount = -(5 + Math.random() * 30);
          break;
        case 'Transportation':
          amount = -(10 + Math.random() * 50);
          break;
        case 'Travel':
          amount = -(100 + Math.random() * 500);
          break;
        case 'Shopping':
          amount = -(20 + Math.random() * 200);
          break;
        default:
          amount = -(5 + Math.random() * 50);
      }
      
      transactions.push({
        transaction_id: `tx_${uuidv4()}`,
        account_id: accountId,
        date: currentDate,
        amount: parseFloat(amount.toFixed(2)),
        name: merchant,
        category: category
      });
    }
  }
  
  return transactions;
}

module.exports = {
  generateMockAccount,
  generateMockTransactions
}; 