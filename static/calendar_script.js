const currentDate = document.querySelector(".current-date"),
daysTag = document.querySelector(".days"),
prevNextIcon = document.querySelectorAll(".icons span");

let date = new Date(),
currYear = date.getFullYear()
currMonth = date.getMonth();

const months = ["Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec", "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień"]

const renderCalendar = () => {
    let firstDayofMonth = new Date(currYear, currMonth, 1).getDay(),   //pierwszy dzień miesiąca
    lastDateofMonth = new Date(currYear, currMonth + 1, 0).getDate(),   //ostatnia data miesiąca
    lastDayofMonth = new Date(currYear, currMonth, lastDateofMonth).getDay(),   //ostatni dzień miesiąca
    lastDateofLastMonth = new Date(currYear, currMonth, 0).getDate();   //ostatnia data poprzedniego miesiąca

    let liTag = "";

    for (let i = firstDayofMonth; i > 0; i--){
        liTag += `<li class="inactive">${lastDateofLastMonth - i + 1}</li>`;
    }

    for (let i = 1; i <= lastDateofMonth; i++){
        let isToday = i === date.getDate() && currMonth === new Date().getMonth() 
                    && currYear === new Date().getFullYear() ? "active" : "";
        liTag += `<li class="${isToday}">${i}</li>`;
    }

    for (let i = lastDayofMonth; i < 6; i++){
        liTag += `<li class="inactive">${i - lastDayofMonth + 1}</li>`;
    }

    currentDate.innerText = `${months[currMonth]} ${currYear}`;
    daysTag.innerHTML = liTag;

    days = document.querySelectorAll(".days li")

days.forEach(day => {
    day.addEventListener("click", () => {
        console.log(day, "clicked", currMonth);
        let currMonth_binary = currMonth;
        if (currMonth - 9 <= 0){
            currMonth_binary = "0"+(currMonth+1);
        }
        window.location.href = `/task/new?deadline=${currYear}-${currMonth_binary}-${day.textContent}`;
        /*const data = {year: currYear, month: currMonth, day: day.textContent};
        fetch('/add-task-cal', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(data)
        })
        .then(response => {
            if (response.ok) {
              console.log('Data wprowadzona');
            } else {
              console.error('Wystąpił błąd podczas wprowadzania daty');
            }
          })
          .catch(error => {
            console.error('Wystąpił błąd:', error);
          });*/
    })
});

}
renderCalendar();


prevNextIcon.forEach(icon => {
    icon.addEventListener("click", () => {
        currMonth = icon.id === "prev" ? currMonth-1 : currMonth+1;

        if(currMonth < 0 || currMonth > 11){
            date = new Date(currYear, currMonth);
            currYear = date.getFullYear();
            currMonth = date.getMonth();
        } else {
            date = new Date();
        }
        renderCalendar();
    })
});

