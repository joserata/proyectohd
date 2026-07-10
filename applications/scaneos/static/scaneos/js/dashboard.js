/*********************************************************************
 * SCANEOS
 * Dashboard
 *********************************************************************/

let scanRunning = false;

let refreshInterval = null;

const csrf =
document.querySelector(
"[name=csrfmiddlewaretoken]"
).value;
async function startScan(){


    const target =
    document.getElementById(
        "target_url"
    ).value.trim();



    if(target===""){


        alert(
            "Ingrese una URL."
        );


        return;

    }



    const formData =
    new FormData();



    formData.append(
        "target",
        target
    );



    document
    .querySelectorAll(
        ".tool-checkbox:checked"
    )
    .forEach(tool=>{


        formData.append(
            "tools",
            tool.value
        );


    });



    scanRunning=true;



    updateStatus(
        "Ejecutando",
        "success"
    );



    addConsole(
        "Inicio escaneo: "
        +target
    );



    try{


        const response =
        await fetch(

            "/scaneos/run/",

            {

                method:"POST",

                headers:{

                    "X-CSRFToken":
                    csrf

                },

                body:formData

            }

        );



        const data =
        await response.json();



        console.log(data);



        if(data.success){


            addConsole(
                "Escaneo completado"
            );


        }
        else{


            addConsole(
                data.message
            );

        }


    }
    catch(error){


        console.error(error);


        addConsole(
            error.message
        );


    }


}
async function stopScan(){

    scanRunning=false;

    updateStatus(
        "Detenido",
        "danger"
    );

    await fetch(

        "/scaneos/stop/",

        {

            method:"POST",

            headers:{

                "X-CSRFToken":csrf

            }

        }

    );

}
function updateStatus(text,color){

    let obj=

    document.getElementById(

        "scanStatus"

    );

    obj.innerHTML=text;

    obj.className=

    "badge bg-"+color+" fs-6";

}
function updateProgress(value){

    const bar=

    document.getElementById(

        "scanProgress"

    );

    bar.style.width=

    value+"%";

    bar.innerHTML=

    value+"%";

}
function addConsole(text){

    let consoleDiv=

    document.getElementById(

        "scanConsole"

    );

    consoleDiv.innerHTML+=

    "<br>"+

    "["+

    new Date()

    .toLocaleTimeString()

    +"] "+text;

    consoleDiv.scrollTop=

    consoleDiv.scrollHeight;

}
async function loadResults(){

    try{

        const response=

        await fetch(

            "/scaneos/results/"

        );

        const data=

        await response.json();

        updateDashboard(data);

    }

    catch(e){

        console.error(e);

    }

}
function updateDashboard(data){

    document.getElementById(

        "riskScore"

    ).innerHTML=

    data.risk;

    document.getElementById(

        "vulnerabilityCount"

    ).innerHTML=

    data.vulnerabilities;

    document.getElementById(

        "attackCount"

    ).innerHTML=

    data.attacks;

    document.getElementById(

        "serviceCount"

    ).innerHTML=

    data.services;

    document.getElementById(

        "lastScan"

    ).innerHTML=

    data.last_scan;

    document.getElementById(

        "nextScan"

    ).innerHTML=

    data.next_scan;

    updateProgress(

        data.progress

    );

}
function updateTable(results){

    let tbody=

    document.querySelector(

        "#resultsTable tbody"

    );

    tbody.innerHTML="";

    results.forEach(item=>{

        tbody.innerHTML+=`

        <tr>

            <td>${item.time}</td>

            <td>${item.tool}</td>

            <td>${item.type}</td>

            <td>${item.severity}</td>

            <td>${item.description}</td>

            <td>${item.status}</td>

            <td>

                <button
                    class="btn btn-sm btn-primary">

                    Ver

                </button>

            </td>

        </tr>

        `;

    });

}
function updateAlerts(alerts){

    let div=

    document.getElementById(

        "alertsContainer"

    );

    div.innerHTML="";

    alerts.forEach(a=>{

        div.innerHTML+=`

        <div class="alert alert-danger">

            <strong>${a.level}</strong>

            ${a.message}

        </div>

        `;

    });

}
function updateEvents(events){

    let div=

    document.getElementById(

        "eventList"

    );

    div.innerHTML="";

    events.forEach(e=>{

        div.innerHTML+=`

        <div class="list-group-item">

            <strong>${e.time}</strong>

            <br>

            ${e.description}

        </div>

        `;

    });

}
function updateServices(services){

    let div=

    document.getElementById(

        "servicesList"

    );

    div.innerHTML="";

    services.forEach(s=>{

        div.innerHTML+=`

        <div class="list-group-item">

            ${s.port}

            -

            ${s.service}

        </div>

        `;

    });

}
refreshInterval=

setInterval(

    ()=>{

        if(scanRunning){

            loadResults();

        }

    },

    5000

);
window.onload=function(){

    loadResults();

};
document.addEventListener(
"DOMContentLoaded",
function(){


    console.log(
        "Dashboard iniciado"
    );


    const btnRunSelected =
    document.getElementById(
        "btnRunSelected"
    );


    if(btnRunSelected){


        btnRunSelected.addEventListener(
            "click",
            function(){

                console.log(
                    "Click ejecutar escaneo"
                );

                startScan();

            }
        );


    }



    const btnRunAll =
    document.getElementById(
        "btnRunAll"
    );


    if(btnRunAll){


        btnRunAll.addEventListener(
            "click",
            function(){

                console.log(
                    "Click ejecutar todos"
                );

                startScan();

            }
        );


    }


});
document.addEventListener(
"DOMContentLoaded",
()=>{


    const btnRun =
    document.getElementById(
        "btnRunSelected"
    );


    if(btnRun){

        btnRun.addEventListener(
            "click",
            startScan
        );

    }



    const btnAll =
    document.getElementById(
        "btnRunAll"
    );


    if(btnAll){

        btnAll.addEventListener(
            "click",
            startScan
        );

    }


});