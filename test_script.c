#include <stdio.h>
#include <string.h>

int main(int argc, char **argv)
{
  //Declare some variables
  FILE *fp; //File Pointer
  int tmpChar; //Single character
  char buff[255]; //Character array
  char gRandFile[50] = "test/g_rand\0";
  char gCPMFile[50] = "test/g_cpm\0";
  char helloFile[50] = "test/hello\0";

  //argv[1] = name of file to open

  //Make sure file chosen is available
  //if(strcmp(argv[1], gRandFile) == 0 || strcmp(argv[1], gCPMFile) == 0 || strcmp(argv[1], helloFile) == 0)
  //{
   // printf("Opening file %s...\n", argv[1]);
  //}
  //else
  //{
    //printf("File %s was not found, try g_rand or g_cpm.\nExiting...\n");
    //return 0;
  //}

  //TESTING OPENING FILE
  //NOT ALLOWED MODES: W, W+, A, R+, A+
  //ALLOWED MODES: R -only
  
  //Tell us if the file was opened
  if((fp = fopen(argv[1], "r")) != NULL)
  {
    printf("%s has been opened successfully!\n", argv[1]);
    
    //Let us try and read the file now
    //Possible read functions: fscanf, fgets, fgetc, fread
    //Each read works a bit differently and should be accounted for
    //by the GFS.
    
    //First we will try to read a single character
    tmpChar = fgetc(fp);
    printf("Attempting read of one character from file %s.\n", argv[1]);
    printf("Character:%c.\n\n", tmpChar);
  }
  else
  {
    printf("Unable to open %s...\nExiting...\n");
  }
  fclose(fp);

  //Attempt to read multiple characters, one at a time
  if((fp = fopen(argv[1], "r")) != NULL)
  {
    printf("Attemping to read all characters one at a time:");
    while((tmpChar = fgetc(fp)) != EOF)
    {
      printf("%c", tmpChar);
    }
    printf(".\n\n");
  }
  else
  {
    printf("Unable to open %s...\nExiting...\n");
  }
  fclose(fp);

  //Attempt to read multiple characters
  if((fp = fopen(argv[1], "r")) != NULL)
  {
    //Attempt to read multiple characters at once (firstline)
    if(fgets(buff, 255, fp) == NULL)
    {
      //Failure
      printf("Unable to read multiple characters from file %s!\nExiting...\n", argv[1]);
    }
    else
    { 
      //Success!
      printf("Successfully read first line from file %s.\n", argv[1]);
      printf("FirstLine(255):%s.\n\n", buff);
      printf("END OF TEST! Exiting...\n\n");
    }
  }
  else
  {
    printf("Unable to open %s...\nExiting...\n");
  }
  fclose(fp);


  return 0;
}
