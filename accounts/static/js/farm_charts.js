function renderFarmCharts(dates, incomes, expenses, pieData) {
    // Line Chart: Income vs Expense
    const trendCtx = document.getElementById('trendChart').getContext('2d');
    new Chart(trendCtx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [
                {
                    label: 'আয় (Income)',
                    data: incomes,
                    borderColor: '#2ecc71',
                    backgroundColor: 'rgba(46, 204, 113, 0.1)',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'ব্যয় (Expense)',
                    data: expenses,
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    fill: true,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'top' } }
        }
    });

    // Pie Chart: Income Sources
    const pieCtx = document.getElementById('incomePieChart').getContext('2d');
    new Chart(pieCtx, {
        type: 'doughnut',
        data: {
            labels: ['দুধ', 'মাংস', 'ডিম'],
            datasets: [{
                data: pieData,
                backgroundColor: ['#3498db', '#e67e22', '#f1c40f'],
                borderWidth: 0
            }]
        },
        options: {
            cutout: '70%',
            plugins: { legend: { position: 'bottom' } }
        }
    });
}