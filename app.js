const dropZone = document.getElementById('dropZone');
const productTable = document.getElementById('productTable');
const resetBtn = document.getElementById('resetBtn');
const warningPopup = document.getElementById('warningPopup');
const urlInputModal = document.getElementById('urlInputModal');
const urlInput = document.getElementById('urlInput');
const cancelUrlInput = document.getElementById('cancelUrlInput');
const submitUrl = document.getElementById('submitUrl');
const urlList = document.getElementById('urlList');
const sustainabilityChart = document.getElementById('sustainabilityChart');

let products = [];
let urls = new Set();
let chart;

window.addEventListener('load', function() {
  const preloader = document.getElementById('preloader');
  setTimeout(() => {
    preloader.style.opacity = '0';
    setTimeout(() => {
      preloader.style.display = 'none';
    }, 500);
  }, 1600);
});

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('bg-eco-green-200');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('bg-eco-green-200');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('bg-eco-green-200');
    const link = e.dataTransfer.getData('text');
    processUrl(link);
});

dropZone.addEventListener('click', () => {
    urlInputModal.classList.remove('hidden');
});

cancelUrlInput.addEventListener('click', () => {
    urlInputModal.classList.add('hidden');
    urlInput.value = '';
});

submitUrl.addEventListener('click', () => {
    const link = urlInput.value.trim();
    if (link) {
        processUrl(link);
        urlInputModal.classList.add('hidden');
        urlInput.value = '';
    }
});

function processUrl(link) {
    if (urls.has(link)) {
        showWarning();
        rejectAnimation();
    } else {
        addProduct(link);
    }
}

// Function to show loader when fetching
function showLoader() {
    document.getElementById('fetch-loader').classList.remove('hidden');
}

// Function to hide loader when fetching is complete
function hideLoader() {
    document.getElementById('fetch-loader').classList.add('hidden');
}


function addProduct(link) {
    showLoader();
    fetch('http://localhost:5000/add_product', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({link}),
    })
        .then(response => response.json())
        .then(updatedProducts => {
            products = updatedProducts;
            urls.add(link);
            updateTable();
            updateChart();
            updateUrlList();
        })
        .catch(error => {
            console.error('Error adding product:', error);
            // showWarning('Failed to add product. Please try again.');
        }).finally(() => {
            hideLoader();
    });
}

function updateTable() {
    const tbody = productTable.querySelector('tbody');
    tbody.innerHTML = '';

    products.forEach((product, index) => {
        const row = tbody.insertRow();
        row.classList.add(index % 2 === 0 ? 'bg-eco-green-100' : 'bg-white');

        const nameCell = row.insertCell();
        nameCell.textContent = truncateText(product.product_name, 30);
        nameCell.classList.add('p-3', 'border-b', 'border-eco-green-200');

        const percentageCell = row.insertCell();
        percentageCell.textContent = product.percentage
            ? `${product.percentage > 0 ? '+' : ''}${product.percentage.toFixed(2)}%`
            : '0%';
        percentageCell.classList.add('p-3', 'border-b', 'border-eco-green-200');
    });
}

function updateChart() {
    if (!sustainabilityChart) {
        console.error('Sustainability chart canvas not found');
        return;
    }

    const ctx = sustainabilityChart.getContext('2d');

    if (chart) {
        chart.destroy();
    }

    const chartData = {
        labels: products.map(p => truncateText(p.product_name, 20)),
        datasets: [{
            label: 'Sustainability Percentage',
            data: products.map(p => p.percentage),
            backgroundColor: 'rgba(102, 187, 106, 0.6)',
            borderColor: 'rgba(102, 187, 106, 1)',
            borderWidth: 1
        }]
    };

    chart = new Chart(ctx, {
        type: 'bar',
        data: chartData,
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Percentage'
                    }
                }
            }
        }
    });
}

function updateUrlList() {
    urlList.innerHTML = '';
    products.forEach(product => {
        const urlElement = document.createElement('a');
        urlElement.href = product.url;
        urlElement.target = '_blank';
        urlElement.textContent = truncateText(product.url, 40);
        urlElement.classList.add('text-eco-green-500', 'hover:text-eco-green-600', 'transition', 'duration-300', 'block', 'mb-2');
        urlList.appendChild(urlElement);
    });
}

function truncateText(text, maxLength) {
    return text.length > maxLength ? text.substring(0, maxLength - 3) + '...' : text;
}

function sortTable(column) {
    products.sort((a, b) => {
        if (a[column] < b[column]) return 1;
        if (a[column] > b[column]) return -1;
        return 0;
    });
    updateTable();
    updateChart();
}

productTable.querySelectorAll('th').forEach(th => {
    th.addEventListener('click', () => {
        const column = th.textContent.toLowerCase().replace(' ', '_');
        sortTable(column);
    });
});

resetBtn.addEventListener('click', () => {
    fetch('http://localhost:5000/reset', {method: 'POST'})
        .then(response => response.json())
        .then(() => {
            products = [];
            urls.clear();
            updateTable();
            updateChart();
            updateUrlList();
        })
        .catch(error => {
            console.error('Error resetting data:', error);
            // showWarning('Failed to reset data. Please try again.');
        });
});

function showWarning(message = 'Duplicate URL rejected!') {
    warningPopup.textContent = message;
    warningPopup.classList.remove('hidden');
    setTimeout(() => {
        warningPopup.classList.add('hidden');
    }, 3000);
}

function rejectAnimation() {
    dropZone.classList.add('animate-shake');
    setTimeout(() => {
        dropZone.classList.remove('animate-shake');
    }, 820);
}

// Initial data population
fetch('http://localhost:5000/get_products')
    .then(response => response.json())
    .then(data => {
        products = data;
        products.forEach(product => urls.add(product.url));
        updateTable();
        updateChart();
        updateUrlList();
    })
    .catch(error => {
        console.error('Error fetching initial data:', error);
        // showWarning('Failed to load initial data. Please refresh the page.');
    });