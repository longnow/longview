if (document.layers) { 
  document.captureEvents(Event.MOUSEMOVE); 
  document.onmousemove = captureMousePosition; 
} else if (document.all) { 
  document.onmousemove = captureMousePosition; 
} else if (document.getElementById) { 
  document.onmousemove = captureMousePosition; 
}

xMousePos = 0;
yMousePos = 0;
xSize = 0;
ySize = 0;

function captureMousePosition(e) { 
  if (document.layers) { 
    xMousePos = e.pageX; 
    yMousePos = e.pageY; 
    xSize = xMousePos - 70;
    ySize = yMousePos + 20;
  } else if (document.all) { 
    xMousePos = window.event.x+document.body.scrollLeft; 
    yMousePos = window.event.y+document.body.scrollTop; 
    xSize = xMousePos - 70;
    ySize = yMousePos + 20;
  } else if (document.getElementById) { 
    xMousePos = e.pageX; 
    yMousePos = e.pageY; 
    xSize = xMousePos - 70;
    ySize = yMousePos + 20;
  } 
}

function showNode(id) {
  document.getElementById('node' + id).style.top = ySize + 'px';
  document.getElementById('node' + id).style.left = xSize + 'px';
  document.getElementById('node' + id).style.visibility = 'visible';
  return true;
}

function hideNode(id) {
  document.getElementById('node' + id).style.visibility = 'hidden';
  return true;
}

var menu;
var theTop = 50;
var old = theTop;

function init()
{
	menu = new getObj('labels');
	movemenu();
}

function movemenu()
{
  if (window.innerWidth)
  {
    pos = window.pageXOffset
  }
  else if (document.documentElement && document.documentElement.scrollLeft)
  {
    pos = document.documentElement.scrollLeft
  }
  else if (document.body)
  {
    pos = document.body.scrollLeft
  }
  if (pos < theTop) pos = theTop;
  else pos += 50;
  if (pos == old)
  {
    menu.style.left = pos;
  }
  old = pos;
  temp = setTimeout('movemenu()',500);
}

function getObj(name)
{
  if (document.getElementById)
  {
  	this.obj = document.getElementById(name);
	  this.style = document.getElementById(name).style;
  }
  else if (document.all)
  {
    this.obj = document.all[name];
    this.style = document.all[name].style;
  }
  else if (document.layers)
  {
   	this.obj = document.layers[name];
   	this.style = document.layers[name];
  }
}
