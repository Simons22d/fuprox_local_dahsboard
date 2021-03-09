$.ajax({
    url: "http://localhost:1000/video/get/all",
    method: "POST",
    data: {
    },
    beforeSend: ()=>{
    },
    success: function (result) {
        console.log("result",result)
    },
    complete : ()=>{
        console.log("done>>>>>")

    }
});