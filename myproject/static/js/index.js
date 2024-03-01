function updateTableUI(containerId, tableStatusArray) {
    const tablesDiv = document.getElementById(containerId);
    tablesDiv.innerHTML = ''; 
    let tableCounter = 0;

    for (let i = 0; i < 6; i++) {
        const rowDiv = document.createElement('div');
        rowDiv.classList.add('row');

        for (let j = 0; j < 3; j++) {
            const status = tableStatusArray[tableCounter];

            if (status === 'empty') {
                rowDiv.innerHTML += '<div class="green"></div>';
            } else if (status === 'occupied') {
                rowDiv.innerHTML += '<div class="red"></div>';
            } else if (status === 'reserved') {
                rowDiv.innerHTML += '<div class="yellow"></div>';
            }
            tableCounter++;
        }
        tablesDiv.appendChild(rowDiv);
    }

}

function updateTableStatus() {
    fetch('/update_table_status')
        .then(response => response.json())
        .then(data => {
            updateTableUI('tablesLeft', data.table_status_array);
            updateTableUI('tablesRight', data.table_status_array2);
            document.getElementById('occupiedPercent').setAttribute('per', data.percentages.occupied);
            document.getElementById('occupiedPercent').style.maxWidth = `${data.percentages.occupied}%`;
            document.getElementById('emptyPercent').setAttribute('per', data.percentages.empty);
            document.getElementById('emptyPercent').style.maxWidth = `${data.percentages.empty}%`;
            document.getElementById('reservePercent').setAttribute('per', data.percentages.reserved);
            document.getElementById('reservePercent').style.maxWidth = `${data.percentages.reserved}%`;
            const messageDisplay = document.getElementById('messageDisplay');
            messageDisplay.innerHTML = `<p>${data.message}</p>`;
        });
}


setInterval(updateTableStatus, 1000);

document.addEventListener('DOMContentLoaded', function () {
    
    updateTableStatus();
});