document.addEventListener("DOMContentLoaded", function (){
    function deleteImage(){
        fetch(delete_url,{
            "method": "POST",
            "headers": {
                "Content-Type": "application/json",
                "X-CSRFToken": csrf_token
            },
            "body": JSON.stringify(img_name)
        }).then(response => response.json()).then(data => {
                if (data.good === true){
                    Swal.fire({
                              icon: "success",
                              title: "Done!",
                              text: "You have deleted the profile image!",
                            }).then(response => {
                                if (response.isConfirmed === true){
                                    location.reload();
                                }else{
                                    location.reload();
                                }
                            });
                }else if (data.noimage === true){
                    Swal.fire({
                              icon: "error",
                              text: "Upload an image first!",
                            });
                }
            });
    }

    document.getElementById('delete-image').addEventListener('click', deleteImage);
    // Facem autosubmit pentru formularul de UploadImage
    document.getElementById('InputImage').addEventListener('input',function(){
        document.getElementById('FormImage').submit();
    });
});
function togg(){
    const data = document.getElementById()
    for (let i=0;i<data.length;i++){
        console.log(data);
        if (data[i].style.display === "none"){
            data[i].style.display = "block";
        }else{
            data[i].style.display = "none";
        }
    }

    }
