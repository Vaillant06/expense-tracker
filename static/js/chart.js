// chart.js

document.addEventListener("DOMContentLoaded", function () {
    // Get category data from the dataset attribute in the HTML
    const categoryData = JSON.parse(
        document.getElementById("expense-chart").dataset.categories
    );

    const ctx = document.getElementById("expense-chart").getContext("2d");

    new Chart(ctx, {
        type: "pie",
        data: {
            labels: Object.keys(categoryData),
            datasets: [
                {
                    label: "Expenses by Category",
                    data: Object.values(categoryData),
                    backgroundColor: [
                        "#FF6384",
                        "#36A2EB",
                        "#FFCE56",
                        "#524f4cff",
                        "#9966FF",
                        "#4BC0C0"
                    ],
                },
            ],
        },
        options: {
            responsive: true,
            responsive: false,
            maintainAspectRatio: false
        },
    });
});
