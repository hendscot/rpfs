#include <stdio.h>

int main(int argc, char **argv)
{
  //Declare some variables
  FILE *fp; //File Pointer
  char tmpchar; //Single character
  char buff[255]; //Character array

  //Get the given file name
  fname = argv[1];

  //Make sure file chosen is available
  switch(fname)
  {
    case "gRand":
    case "gCPM":
      printf("Opening file %s...\n", fname);
    break;

    default:
      printf("File %s was not found, try gRAND or gCPM.\nExiting...\n");
      return 0;
    break;
  }

  //TESTING OPENING FILE
  //NOT ALLOWED MODES: W, W+, A, R+, A+
  //ALLOWED MODES: R -only
  fp = fopen(fname, "w+"); 
  
  //Tell us if the file was opened
  if(fp != 0)
  {
    printf("%s has been opened successfully!\n", fname);
    
    //Let us try and read the file now
    //Possible read functions: fscanf, fgets, fgetc, fread
    //Each read works a bit differently and should be accounted for
    //by the GFS.
    
    //First we will try to read a single character
    char tmpChar = fgetc(fp);
    
    //Check to see if we have "EOF" or a character...
    if(tmpChar == "EOF")
    {
      printf("Unable to read character from file %s!\nExiting...\n", fname);
      fclose(fp);
    }
    else
    {
      printf("Successfully read character from file %s: %s \n", fname, tmpChar);
      
      //Attempt to read multiple characters
      if(fgets(buff, 255, fp) == NULL)
      {
        //Failure
        printf("Unable to read multiple characters from file %s!\nExiting...\n", fname);
      }
      else
      { 
        //Success!
        printf("Successfully read multiple characters from file %s: %s \n", fname, buff);
        printf("END OF TEST! Exiting...\n");
      }
    }
    
  }
  else
  {
    printf("Unable to open %s...\nExiting...\n");
    return 0;
  }


  //Close the file
  fclose(fp);

  return 0;
}
