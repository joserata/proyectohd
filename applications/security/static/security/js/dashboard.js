/********************************************************************
 * DEVSECOPS CENTER
 * dashboard.js
 ********************************************************************/

let reports = {};

const csrf =
document.querySelector("[name=csrfmiddlewaretoken]").value;

const tools = [

    "bandit",
    "semgrep",
    "safety",
    "pip_audit",
    "pylint",
    "flake8",
    "black",
    "mypy",
    "detect_secrets",
    "radon",
    "xenon",
    "coverage",
    "playwright",
    "locust",
    "pytest",
    "pip_licenses",
    "cyclonedx",
    "yara",
    "wapiti"

];



/************************************************************
 EJECUTAR UNA HERRAMIENTA
************************************************************/

async function runTool(tool){

    const url=document.getElementById("target_url").value;

    setStatus(tool,"Ejecutando...","warning");

    const start=performance.now();

    try{

        const response=await fetch(

            "/security/run/"+tool+"/",

            {

                method:"POST",

                headers:{

                    "X-CSRFToken":csrf,

                    "Content-Type":
                    "application/x-www-form-urlencoded"

                },

                body:new URLSearchParams({

                    target_url:url

                })

            }

        );

        const data=await response.json();

        if(!data.success){

            alert(data.message);

            return;

        }

        reports[tool]=data;

        updateCard(tool,data);

        addHistory(data);

    }

    catch(e){

        console.error(e);

        setStatus(tool,"Error","danger");

    }

    finally{

        console.log(

            tool,

            performance.now()-start

        );

    }

}



/************************************************************
 EJECUTAR TODAS
************************************************************/

async function runAll(){

    disableButtons(true);

    for(const tool of tools){

        await runTool(tool);

    }

    disableButtons(false);

}



/************************************************************
 ACTUALIZA TARJETA
************************************************************/

function updateCard(tool,data){

    document.getElementById(

        tool+"_status"

    ).innerHTML=data.status;

    document.getElementById(

        tool+"_duration"

    ).innerHTML=data.duration+" s";

    document.getElementById(

        tool+"_findings"

    ).innerHTML=data.findings;

}



/************************************************************
 CAMBIA COLOR
************************************************************/

function setStatus(tool,text,color){

    let obj=document.getElementById(

        tool+"_status"

    );

    obj.innerHTML=text;

    obj.className="badge bg-"+color;

}



/************************************************************
 HABILITA BOTONES
************************************************************/

function disableButtons(disabled){

    document

    .querySelectorAll("button")

    .forEach(

        b=>b.disabled=disabled

    );

}



/************************************************************
 ABRIR REPORTE
************************************************************/

function openReport(tool){

    if(!(tool in reports)){

        alert(

            "Debe ejecutar primero esta herramienta."

        );

        return;

    }

    document.getElementById(

        "reportModal"

    ).style.display="block";

    document.getElementById(

        "modalTitle"

    ).innerHTML=tool.toUpperCase();

    document.getElementById(

        "modalRecommendation"

    ).innerHTML=

    reports[tool].recommendation;

    document.getElementById(

        "modalOutput"

    ).textContent=

    reports[tool].output;

}



/************************************************************
 CERRAR REPORTE
************************************************************/

function closeReport(){

    document.getElementById(

        "reportModal"

    ).style.display="none";

}



/************************************************************
 DESCARGAR JSON
************************************************************/

function downloadReport(tool){

    if(!(tool in reports)){

        return;

    }

    let blob=new Blob(

        [

            JSON.stringify(

                reports[tool],

                null,

                4

            )

        ],

        {

            type:"application/json"

        }

    );

    let a=document.createElement("a");

    a.href=URL.createObjectURL(blob);

    a.download=

    tool+"_report.json";

    a.click();

}



/************************************************************
 EXPORTAR TODOS
************************************************************/

function downloadAll(){

    let blob=new Blob(

        [

            JSON.stringify(

                reports,

                null,

                4

            )

        ],

        {

            type:"application/json"

        }

    );

    let a=document.createElement("a");

    a.href=URL.createObjectURL(blob);

    a.download="SecurityReport.json";

    a.click();

}



/************************************************************
 HISTORIAL
************************************************************/

function addHistory(data){

    const tbody=

    document.querySelector(

        "#historyTable tbody"

    );

    if(!tbody){

        return;

    }

    let row=tbody.insertRow(0);

    row.innerHTML=`

        <td>${data.tool}</td>

        <td>${data.status}</td>

        <td>${data.duration}</td>

        <td>${data.findings}</td>

        <td>${new Date().toLocaleString()}</td>

    `;

}



/************************************************************
 BUSCAR
************************************************************/

function filterCards(){

    const txt=

    document.getElementById(

        "searchTool"

    ).value.toLowerCase();

    document

    .querySelectorAll(".tool-card")

    .forEach(card=>{

        card.style.display=

        card.innerText

        .toLowerCase()

        .includes(txt)

        ?

        "block"

        :

        "none";

    });

}



/************************************************************
 AUTO REFRESH
************************************************************/

setInterval(()=>{

    console.log(

        "DevSecOps Dashboard"

    );

},60000);