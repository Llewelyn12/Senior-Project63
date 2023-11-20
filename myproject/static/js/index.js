const seatsContainer = document.getElementById('seats-container');

class Seat {
    constructor(row, col) {
        this.row = row;
        this.col = col;
    }
}

seatsobjArr = [];

for (let i = 0; i < 5; i++) {
    for (let j = 0; j < 8; j++) { 
        seatsobjArr.push(new Seat(i, j, false))
    }
}

seatsobjArr.forEach(seat => {
    const seatDiv = document.createElement('div');
    seatDiv.classList.add('seat');
    seatDiv.classList.add(`row-${seat.row}`);
    seatDiv.classList.add(`col-${seat.col}`);
    
    if (seat.col >= 0 && seat.col <= 2) {
        seatDiv.style.backgroundColor = 'green'; 
    } else if (seat.col >= 3 && seat.col <= 4) {
        seatDiv.style.backgroundColor = 'transparent'; 
    } else if (seat.col >= 5 && seat.col <= 7) {
        seatDiv.style.backgroundColor = 'red';
    }

    seatsContainer.appendChild(seatDiv);
});



console.log(seatsobjArr)