var map;

var latitude = -1.18063845;
var longitude = 36.9309979520277;
var map;

let searchHandle = document.getElementById("searchPlace")
let handle = document.getElementById('map')
let datalist = $("#searcher")


const fowardSearch = (term) => {
    $.ajax({
        url : `https://eu1.locationiq.com/v1/search.php?key=af236a4eb6f160&q=${term}&format=json`,
        method : "GET",
        beforeSend : ()=>{
        },
        success : (data) =>{
            console.log(">>>",data)
            // add data to the datalist
            data.map((index,item)=>{
                datalist.html(`<option value='${index.display_name}'>${index.osm_type}</option>`);
            })
        },
        error : (error)=>{
            console.error(error)
        }
    })
}

searchHandle.addEventListener("input",(e)=>{
    fowardSearch(e.target.value)
})

searchHandle.addEventListener("keyup",(e)=>{
    $.ajax({
        url : `https://eu1.locationiq.com/v1/search.php?key=af236a4eb6f160&q=${e.target.value}&format=json`,
        method : "GET",
        beforeSend : ()=>{
        },
        success : (data) =>{

            // add data to the datalist
             // here wea re going t o add the dat to the DOM
            if(data){
            //     get the first item an add the data to the DOM
                let first_item = data[0];
                $("#suggestLocation").val(first_item.display_name)
                $("#lat").val(first_item.lat)
                $("#long").val(first_item.lon)
                map.setCenter(new google.maps.LatLng(first_item.lat, first_item.lon))
                    var marker = new google.maps.Marker({
                        position: new google.maps.LatLng(first_item.lat, first_item.lon),
                        map: map,
                        title: first_item.display_name
                    });

            }
        },
        error : (error)=>{
            // console.error(error)
        }
    })
})




function initMap() {
    var myLatLng = {lat: latitude, lng: longitude};

    map = new google.maps.Map(handle, {
        center: myLatLng,
        zoom: 15,
        disableDoubleClickZoom: true, // disable the default map zoom on double click
    });

    // Update lat/long value of div when anywhere in the map is clicked    
    google.maps.event.addListener(map, 'click', function (event) {
        let lat = event.latLng.lat();
        let long = event.latLng.lng();
        // document.getElementById('latclicked').innerHTML = event.latLng.lat();
        // document.getElementById('longclicked').innerHTML = event.latLng.lng();
        // get the coordinate of the location on map and save it to the database
        geoCodeRequest(event.latLng.lat(), event.latLng.lng());
    });


    var marker = new google.maps.Marker({
        position: myLatLng,
        map: map,
        //title: 'Hello World'

        // setting latitude & longitude as title of the marker
        // title is shown when you hover over the marker
        title: latitude + ', ' + longitude
    });

    // Update lat/long value of div when the marker is clicked
    marker.addListener('click', function (event) {
        let lat = event.latLng.lat();
        let long = event.latLng.lng();
        // document.getElementById('latclicked').innerHTML = lat;
        // document.getElementById('longclicked').innerHTML = long;
    });

    // Create new marker on double click event on the map
    google.maps.event.addListener(map, 'dblclick', function (event) {
        var marker = new google.maps.Marker({
            position: event.latLng,
            map: map,
            title: event.latLng.lat() + ', ' + event.latLng.lng()
        });

        // // Update lat/long value of div when the marker is clicked
        // marker.addListener('click', function () {
        //     console.log("LAT",event.latLng.lat)
        //     consol.elog("LONG",event.latLng.lng())
        //     // document.getElementById('latclicked').innerHTML = event.latLng.lat();
        //     // document.getElementById('longclicked').innerHTML = event.latLng.lng();
        // });

        // Create new marker on single click event on the map
        // google.maps.event.addListener(map, 'click', function (event) {
        //     var marker = new google.maps.Marker({
        //         position: event.latLng,
        //         map: map,
        //         title: event.latLng.lat() + ', ' + event.latLng.lng()
        //     });
        // });
    })
}

const geoCodeRequest = (lat,long) =>{
    let key = "af236a4eb6f160";
    let locationData = geoCode(key,lat,long); 
    return locationData;
}

/*
address ....
https://eu1.locationiq.com/v1/reverse.php?key=YOUR_PRIVATE_TOKEN&lat=LATITUDE&lon=LONGITUDE&format=json
*/


const geoCode = (apiKey,lat,long) =>{
    $.ajax({
        url : `https://eu1.locationiq.com/v1/reverse.php?key=${apiKey}&lat=${lat}&lon=${long}&format=json`,
        method : "GET",
        beforeSend : ()=>{
            // show loading ... 
        },
        success : (data) =>{
            $("#suggestLocation").val(data.display_name);
            $("#long").val(data.lon)
            $("#lat").val(data.lat);
        },
        error : (error)=>{
        }
    })

}


// get handle for search
