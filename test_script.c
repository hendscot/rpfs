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
  fp = fopen(argv[1], "r"); 
  
  //Tell us if the file was opened
  if(fp != NULL)
  {
    printf("%s has been opened successfully!\n", argv[1]);
    
    //Let us try and read the file now
    //Possible read functions: fscanf, fgets, fgetc, fread
    //Each read works a bit differently and should be accounted for
    //by the GFS.
    
    //First we will try to read a single character
    tmpChar = fgetc(fp);
    printf("Successfully read character from file %s: %c \n", argv[1], tmpChar);
      
    //Attempt to read multiple characters
    if(fgets(buff, 5, fp) == NULL)
    {
      //Failure
      printf("Unable to read multiple characters from file %s!\nExiting...\n", argv[1]);
    }
    else
    { 
      //Success!
      printf("Successfully read multiple characters from file %s: %s \n", argv[1], buff);
      printf("END OF TEST! Exiting...\n");
    }

    //Close the file
    fclose(fp);
  }
  else
  {
    printf("Unable to open %s...\nExiting...\n");
  }

  return 0;
}
