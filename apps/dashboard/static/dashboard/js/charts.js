$(document).ready(function () {
    $.ajax({
        url: "/chart/filter-options/",
        type: "GET",
        dataType: "json",
        success: (jsonResponse) => {
            // Load all the options
            jsonResponse.options.forEach(option => {
                $("#year").append(new Option(option, option));
            });
            // Load data for the first option
            // loadAllCharts($("#year").children().first().val());
            loadAllCharts(2023);
        },
        error: () => console.log("Failed to fetch chart filter options!")
    });
});

// $("#filterForm").on("submit", (event) => {
//     alert(year);
//
//     event.preventDefault();
//
//     const year = $("#year").val();
//     // loadAllCharts(2023)
// });


function loadChart(chart, endpoint) {
    $.ajax({
        url: endpoint,
        type: "GET",
        dataType: "json",
        success: (jsonResponse) => {
            // Extract data from the response
            const title = jsonResponse.title;
            const labels = jsonResponse.data.labels;
            const datasets = jsonResponse.data.datasets;

            // Reset the current chart
            chart.data.datasets = [];
            chart.data.labels = [];

            // Load new data into the chart
            chart.options.title.text = title;
            chart.options.title.display = true;
            chart.data.labels = labels;
            datasets.forEach(dataset => {
                chart.data.datasets.push(dataset);
            });
            chart.update();
        },
        error: () => alert("Failed to fetch chart data from " + endpoint + "!")
    });
}

function loadAllCharts(year) {
    try {
        loadChart(customersChart, `/chart/customers/${year}/`);
    } catch (e) {
    }

    try {
        loadChart(employeesChart, `/chart/employees/${year}/`);
    } catch (e) {
    }
    try {
        loadChart(planChart, `/chart/plan/${year}/`);
    } catch (e) {
    }
    try {
        loadChart(verificationsChart, `/chart/customers/${year}/`);
    } catch (e) {
    }
    try {
        loadChart(usersChart, `/chart/users/${year}/`);
    } catch (e) {
    }
    try {
        loadChart(paymentsChart, `/chart/payments/${year}/`);
    } catch (e) {
    }
    try {
        loadChart(ticketsChart, `/chart/tickets/${year}/`);
    } catch (e) {
    }
}