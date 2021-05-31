let thisVal;
// let lnk = "localhost"
function getFrequency(item){
    thisVal =  item.value;
    if(thisVal === "null"){
        $("#type").prop("disabled",true);
        $("#statusOne").prop("selected",true);
    }else if(thisVal === 'day'){
        $("#type").removeAttr("disabled");
        $("#dateCont").show();
        $("#monthCont").hide();
        $("#weekCont").hide();
    }else if(thisVal === "week"){
        $("#type").removeAttr("disabled");
        $("#dateCont").hide();
        $("#monthCont").show();
        $("#weekCont").show();

    }else if(thisVal === 'month'){
        $("#type").removeAttr("disabled");
        $("#dateCont").hide();
        $("#monthCont").show();
        $("#weekCont").hide();
    }
}

const daysInMonth  = (month, year) => {
    return new Date(year, month, 0).getDate();
}

const generateReport = (data, title = "") => {
    // get the table handle
    let handle = $("#report");
    if (title !== "") {
        handle.append(`<tr><td>${title}</td></tr>`)
    }
    // working with the report data
    // mappiong begins
    mapper =["Local","Online","Instant"]
    data.map((value, key) => {
        let id = value.id;
        let branch_id = value.branch_id;
        let active_ = value.active ? "Active" : "Serviced";
        let forwarded = value.forwarded ? "Fowarded": "Not Forwarded";
        let kind = mapper["kind"];
        let service_name = value.service_name;
        let serviced = value.serviced;
        let start = value.start;
        let teller = value.teller;
        let user = value.user;

        handle.append(
            `<tr class="asset" onclick="" id="${id}">
                    <th data-id="${id}">${id}</th>
                    <td data-id="${id}">${branch_id}</td>
                    <td data-id="${id}">${active_}</td>
                    <td data-id="${id}">${forwarded}</td>
                    <td data-id="${id}">${kind}</td>
                    <td data-id="${id}">${service_name}</td>
                    <td data-id="${id}">${serviced}</td>
                    <td data-id="${id}">${start}</td>
                    <td data-id="${id}">${teller}</td>
                    <td data-id="${id}">${user}</td>
                </tr>`)
    })
}


const updateWeek = (item) => {
    let month = $("#month").val()
    if(month !== ""){
        let daysInMonths = new Date(month);
        let yearDate = daysInMonths.getFullYear();
        let monthDate = daysInMonths.getMonth()+1;
        var days = daysInMonth(monthDate,yearDate);
        let weeks = Math.floor(days/7);
        let extraDays = days%7;
        if(extraDays > 0){
            // five weeks
            $("#five").show();
        }else{
            // four weeks
            $("#five").hide();
        }
    }else{
        let error = $("#error");
        let monthHandle = $("#month");
        error.html("Month Required. Please Select Select A Month")
        error.show();
        monthHandle.addClass("is-invalid")
        setTimeout(()=>{
            error.hide()
            monthHandle.removeClass("is-invalid")
        },5000);
    }
}


var start = new Date(),
            prevDay,
            startHours = 8;
// 09:00 AM
start.setHours(8);
start.setMinutes(0);
// If today is Saturday or Sunday set 10:00 AM
if ([6, 0].indexOf(start.getDay()) !== -1) {
    start.setHours(10);
    startHours = 10
}
// var minHours =;
// var minDate = ;
// minDate : today;
$('#date_range').datepicker({
    language: 'en',
    startDate: start,
    maxDate: start,
    autoClose: true,
    position: "top left",
    onSelect: function (fd, d, picker) {
        // Do nothing if selection was cleared
        if (!d) return;
        let day = d.getDay();
        // Trigger only if date is changed
        if (prevDay !== undefined && prevDay === day) return;
        prevDay = day;
        // If chosen day is Saturday or Sunday when set
        // hour value for weekends, else restore defaults
        if (day === 6 || day === 0) {
            picker.update({
                minHours: 10,
                maxHours: 16
            })
        } else {
            picker.update({
                minHours: 9,
                maxHours: 18
            })
        }
    }
});


$('#month').datepicker({
language: 'en',
startDate: start,
autoClose : true,
view : "months",
minView : "months",
maxDate : start,
dataMinView : "months",
dataView : "months",
position: "top left",
onSelect: function (fd, d, picker) {
    // Do nothing if selection was cleared
    if (!d) return;
    var day = d.getDay();
    // Trigger only if date is changed
    if (prevDay !== undefined && prevDay === day) return;
    prevDay = day;
    // If chosen day is Saturday or Sunday when set
    // hour value for weekends, else restore defaults
    if (day === 6 || day === 0) {
        picker.update({
            minHours: 10,
            maxHours: 16
        })
    } else {
        picker.update({
            minHours: 9,
            maxHours: 18
        })
    }
}
});


$('#generate').on("click",()=>{
    // generics
    let period = $("#frequency").val();
    let status = $("#type").val();
    let date
    if(thisVal === "day"){
        date = $("#dailyCal").val();
    }else if(thisVal === "month"){
        date = $("#month").val()
    }

    // getting the date info
    if(status && period  && date){
        // date variables
        let month, week, newDay;
        let errorHandle = $("#error");
        let generate = $("#generate");
        let generating = $("#generating");
        let done = $("#done");

        // get new date
        console.log("Date",date)

        let unformattedDate = date.split("/").join("-").split("-");
        let formattedDate = unformattedDate[2]+"-"+unformattedDate[0]+"-"+unformattedDate[1];
        let data= JSON.stringify({
                duration : period,
                kind : status,
                date : formattedDate
            })

        // we are going to make an ajax request based on the data
        $.ajax({
            url: `http://${lnk}:3000/dashboard/reports`,
            method: "POST",
            contentType:"application/json; charset=utf-8",
            dataType:"json",
            data: data,
            beforeSend: ()=>{
                $("#spinner").show();
                done.hide();
                generating.show();
                generate.prop("disabled",true)
            },
            success: function (result) {
                generateReport(result,"Report Data");
                    setTimeout(()=>{
                        let statusMapper = ["New Issues","Assigned Issues","Resolved Issues","Closed Issues","","Escalated Issues","All Issues — {New, Assigned, Resolved,Escalated,Closed}"];
                        let name = `${new Date().getUTCDate()}__${period}__${statusMapper[status]}.xlsx`;
                        //  excel gen
                        excel = new ExcelGen({
                            "src_id": "report",
                            "show_header": true,
                            "format": "xlsx",
                        });

                        excel.generate(name);
                        // end excel gen

                            $("#generating").hide()
                            errorHandle.show();
                            setTimeout(()=>{
                                $('#error').hide();
                                $("#generate").prop("disabled",false)
                            },5000);
                        },500)
                // }
            },
            complete : ()=>{
                setTimeout(()=>{ $("#spinner").hide()} ,1000)
            }
        });
        // fethch()
    }else{
        $("#done").hide()
        function error(id,msg){
            let handle = $("#error");
            handle.html(msg)
            handle.show();
            $(`#${id}`).addClass("is-invalid")
            setTimeout(()=>{
                handle.hide()
                $(`#${id}`).removeClass("is-invalid")
            },5000);
        }
        // some data is not set
        if(period === "null"){
            error("frequency","Duration Is Required.");
        } else if(status === "null"){
            error("type","Issue Type Is Required");
        }else if(!date){
            error("date","Date is Required");
        }
    }
});
// Here we are going to update the graphs

const statusChange = (me)=>{
    let option = me.value
    let timer = $("#tickets_reset_div")
    $("#reset_message").html("")
    if(Number(option) === 1){
        timer.show()
    }else if(Number){
        timer.hide()
    }
}


$("#reset_message").html("")
const update_reset_settings = () =>{
    let options_reset = $("#options_reset").val();
    let reset_time= $("#reset_time").val();
    console.log(options_reset,reset_time,reset_time.trim().length)
    if (Number(options_reset) === 1) {
        if(reset_time.trim().length === 5){
            $("#reset_message").html("")
            let option = Number(options_reset) === 1  ? true : false;
            let time = reset_time
            console.log(option,time)
            getData(`http://${loc}:9000/reset/settings`,"POST",{"option" : option,"time" : time},(data)=>{
                console.log(data)
                window.location.href = `http://${loc}:9000/extras`
            })
        }else{
            $("#reset_message").html(`<div class="alert alert-warning" role="alert">Error! Time is
                  required</div>`)
        }
    }else if(Number(options_reset) === 2){
        // we can work without reseting the tickets
        getData(`http://${loc}:9000/reset/settings`,"POST",{"option" : false,"time" :'00:00'},(data)=>{
                window.location.href = `http://${loc}:9000/extras`
        })
    }

}


setTimeout(()=>{
        $('#reset_time').clockpicker({
			placement: 'top',
			donetext : "Select Time"
		});
    },2000)




$("#search_bookings").on("input",(e)=>{
   let search_term = $("#search_bookings").val()
	console.log(search_term)
    getData(`http://${window.location.hostname}:9000/booking/search`,"POST",{"term" : search_term},(data)=>{
        
        let item = ""

        if(data.length){
            data.map((booking,index)=>{
                console.log(booking)
                item += `<tr>
                <td>${ booking.id }</td>
                <td>${ booking.start }  ${ booking.ticket }</td>
                <td>${ booking.service_name } </td>
                <td>${ booking.teller } </td>
                <td>${ booking.serviced  ? "Serviced" : "Not Serviced" }</td>
                <td>${ booking.is_synced ?  "Synced"  : "Not Synced" }</td>
                <td>${ booking.forwarded  ?  "Forwarded"  :  "Not Forwarded" }</td>
                <td title="${booking.date_added}">${ booking.date_term }</td>
                <td><a href="/bookings/details/${ booking.id }">Details</a></td>
              </tr>`
            })
        }else{
        //    get all
            if(search_term.length){
                item = ("<h5>Empty</h5><p>No records on the keyword.</p>")
            }else{
                let item_ = ""
                getData(`http://${window.location.hostname}:9000/bookings/all`,"POST",{"term" : search_term},(data_)=>{
                    data_.map((booking,index)=>{
                        console.log(booking)
                        item_ += `<tr>
                        <td>${ booking.id }</td>
                        <td>${ booking.start }  ${ booking.ticket }</td>
                        <td>${ booking.service_name } </td>
                        <td>${ booking.teller } </td>
                        <td>${ booking.serviced  ? "Serviced" : "Not Serviced" }</td>
                        <td>${ booking.forwarded  ?  "Forwarded"  :  "Not Forwarded" }</td>
                        <td>${ booking.is_synced ?  "Synced"  : "Not Synced" }</td>
                        <td title="${booking.date_added}">${ booking.date_term }</td>
                        <td><a href="/bookings/details/${ booking.id }">Details</a></td>
                      </tr>`
                    })
                    $('#adminTableBody').html(item_)
                 })
            }
        }
        $('#adminTableBody').html(item)
    })


})


$("#download_apps").on("click",()=>{
    let application = $("#application").val()
    // let platform = $("#platform").val()
    let filename = "Windows_"+application
    window.location.href = `http://159.65.144.235:3000/app/download/${filename}.msi`
})



