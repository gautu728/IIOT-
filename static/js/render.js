

function renderDropdowns(){
  var list=['component','modelName','operations']
  var component=['hsgag','ihfew','iwgja']
  var modelName=['whar']
  var operations=['wiroq']
  var all=[component,modelName,operations]
  for (let index = 0; index < list.length; index++) {
        const idName = list[index];
        if(index==0)
        {
              component.forEach(element => {
                  var dropdown = document.getElementById(idName);
                  var opt = document.createElement("option"); 
                  opt.text = element;
                  opt.value = element;
                  dropdown.options.add(opt);       
              });
        }
        else if(index==1){
            modelName.forEach(element => {
                  var dropdown = document.getElementById(idName);
                  var opt = document.createElement("option"); 
                  opt.text = element;
                  opt.value = element;
                  dropdown.options.add(opt);       
              });
        }
        else{
            operations.forEach(element => {
                  var dropdown = document.getElementById(idName);
                  var opt = document.createElement("option"); 
                  opt.text = element;
                  opt.value = element;
                  dropdown.options.add(opt);       
              });    
        }
        
  }
  
}
