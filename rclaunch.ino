bool readerror=false;

bool launchlock=false;
int lastlaunch=0;

void setup() {
pinMode(2, INPUT);
pinMode(3, INPUT);


pinMode(4, OUTPUT);
pinMode(5, OUTPUT);
pinMode(6, OUTPUT);
pinMode(7, OUTPUT);
pinMode(8, OUTPUT);
pinMode(9, OUTPUT);
pinMode(10, OUTPUT);
pinMode(11, OUTPUT);
pinMode(12, OUTPUT);
pinMode(13, OUTPUT);

digitalWrite(4,LOW);
digitalWrite(5,LOW);
digitalWrite(6,LOW);
digitalWrite(7,LOW);
digitalWrite(8,LOW);
digitalWrite(9,LOW);
digitalWrite(10,LOW);
digitalWrite(11,LOW);
digitalWrite(12,LOW);
digitalWrite(13,LOW);


Serial.begin(9600);
}

void loop() {
  
  int ch1 = pulseIn(3, HIGH); //read the pulse width of each channel
  int ch2 = pulseIn(2, HIGH);
  if(ch1==0||ch2==0) readerror=true;
  //Serial.print(ch1);
  //Serial.print("   ");
  //Serial.print(ch2);
  //Serial.print("   ");
  ch1=map(ch1, 1073,1974,-100,100);//tested max limits of each channel
  ch2=map(ch2, 987,1961,-100,100);
  //Serial.print(ch1);
  //Serial.print("   ");
  //Serial.print(ch2);
  //Serial.println("");
  
  if(readerror==true){
    keeplow();
    Serial.println("Channel Read Error");
    int ch1 = pulseIn(3, HIGH); //read the pulse width of each channel
    int ch2 = pulseIn(2, HIGH);
    readerror=false;
    if(ch1==0||ch2==0) readerror=true;
  }
  
  if(readerror==false){
    int launchnum = determinelaunch(ch1,ch2);
    if (lastlaunch==0){
      launchlock=false;
    }
    if (lastlaunch>0){
      launchlock=true;
      }
    if(launchlock==false){
      if(launchnum>0) {
        Serial.println(launchnum);
        actuallylaunch(launchnum);
      }
      if(launchnum==0) Serial.println("waiting");
    }
     lastlaunch=launchnum;
  }
}






int determinelaunch(int wheel, int trigger){
  if(wheel>-33 && wheel<33 && trigger>-50 && trigger<50) return 0;

  if(wheel>-110 && wheel<=-66 && trigger>50 && trigger<110) return 1;
  if(wheel>-66 && wheel<=-15 && trigger>50 && trigger<110) return 2;
  if(wheel>-15 && wheel<=15 && trigger>50 && trigger<110) return 3;
  if(wheel>15 && wheel<=66 && trigger>50 && trigger<110) return 4;
  if(wheel>66 && wheel<=110 && trigger>50 && trigger<110) return 5;
  
  if(wheel>-110 && wheel<=-66 && trigger>-110 && trigger<-50) return 6;
  if(wheel>-66 && wheel<=-15 && trigger>-110 && trigger<-50) return 7;
  if(wheel>-15 && wheel<=15 && trigger>-110 && trigger<-50) return 8;
  if(wheel>15 && wheel<=66 && trigger>-110 && trigger<-50) return 9;
  if(wheel>66 && wheel<=110 && trigger>-110 && trigger<-50) return 10;
   
  return 0;
                  
}

void keeplow(void){
  digitalWrite(4,LOW);
  digitalWrite(5,LOW);
  digitalWrite(6,LOW);
  digitalWrite(7,LOW);
  digitalWrite(8,LOW);
  digitalWrite(9,LOW);
  digitalWrite(10,LOW);
  digitalWrite(11,LOW);
  digitalWrite(12,LOW);
  digitalWrite(13,LOW);
  
}

void actuallylaunch(int launchnum){
  int digport=14-launchnum;
  digitalWrite(digport,HIGH);
  delay(1050);
  keeplow();
}
