const date = new Date().toJSON().slice(0, 10)
console.log(date)
document.getElementById("date").max = date


function Verification() {

    var date = document.getElementById('date').value

    var datelen = date.length
    var name = document.getElementById('Sname').value

    var namelen = name.length

    if (datelen > 0 && namelen > 0) {
        return true
    } else {
        return false
    }
    
   

}


