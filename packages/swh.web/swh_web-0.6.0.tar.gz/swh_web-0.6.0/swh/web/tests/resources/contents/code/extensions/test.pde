import java.util.LinkedList;
import java.awt.Point;

PGraphics pg;
String load;

void setup() {
  size(displayWidth, displayHeight, P3D);
  pg = createGraphics(displayWidth*2,displayHeight,P2D);
  pg.beginDraw();
  pg.background(255,255,255);
  //pg.smooth(8);
  pg.endDraw();
}
void draw(){
  background(255);
}

