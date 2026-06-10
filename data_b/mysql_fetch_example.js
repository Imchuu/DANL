const mysql = require('mysql2/promise');

async function fetchData() {
  const config = {
    host: '58.187.108.102',
    port: 3306,
    user: 'maipn',
    password: 'Maipn123@',
    database: 'pvn',
  };

  let connection;

  try {
    connection = await mysql.createConnection(config);
    const [rows] = await connection.execute('SELECT * FROM customers LIMIT 10');

    console.log(rows);
  } catch (err) {
    console.error('Lỗi khi kết nối MySQL:', err.message);
  } finally {
    if (connection) {
      await connection.end();
    }
  }
}

fetchData();
