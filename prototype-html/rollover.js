
var current;
var currentoff;
var imgloaded = false;

function loadimgs() 
{
  if (document.images) 
  {
    load1 = newimg("img-static/nav-on.gif");        
    load2 = newimg("img-generated/nav-now-on.png");        
    load3 = newimg("img-generated/nav-now-off.png");        
    imgloaded = true;
    onimgs('navnow', 'img-generated/nav-now-on.png',
           'img-generated/nav-now-off.png');
  }
}

function newimg(arg) 
{
   if (document.images) 
   {
        thisimg = new Image();
        thisimg.src = arg;
        return thisimg;
   }
}

function chimgs() 
{
   if (document.images && (imgloaded == true)) 
   {
      for (var i=0; i<chimgs.arguments.length; i+=2) 
      {
        if (chimgs.arguments[i] != current)
        {
          document[chimgs.arguments[i]].src = chimgs.arguments[i+1];
        }
      }   
   }
}

function onimgs() 
{
  if (document.images && (imgloaded == true)) 
  {
  
    if (current && currentoff)
    {
      document[current].src = currentoff;
    }
        
    for (var i=0; i<onimgs.arguments.length; i+=3) 
    {
      current = onimgs.arguments[i];
      currentoff = onimgs.arguments[i+2];
      document[onimgs.arguments[i]].src = onimgs.arguments[i+1];
    }
  }
}

