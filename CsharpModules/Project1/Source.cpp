// Base class
#include <string>
#include<iostream>
#include <fstream>

using namespace std;
class Animal {
public:
    virtual void animalSound() {
        cout << "The animal makes a sound \n";
    }
    virtual void printSpeed() = 0;

};

// Derived class
class Pig : public Animal {
public:
    void animalSound() {
        cout << "The pig says: wee wee \n";
    }
    void printSpeed() override
    {
        cout << "ehehhehe";
    }

};

// Derived class
class Dog : public Animal {
public:

    void animalSound() {
        cout << "The dog says: bow wow \n";
    }
    void printSpeed() override
    {
        cout << "hohohhohoho";
    }
    void writeToFIle(string filePath,string whatToWrite)
    {
        
            ofstream fileWriter(filePath);
            fileWriter << whatToWrite << endl;
            fileWriter.close();
        
    }
    void readFromFile(string filePath)
    {
        try
        {
        ifstream fileReader(filePath);
        string myText;
        while (getline(fileReader, myText))
        {
            cout << myText;
        }
        throw std::exception_ptr();
        }
    catch (std::invalid_argument &e)
    {
        cout << "file can not be opened";
        cout << endl << e.what() << endl;
        
    }
    catch (std::exception_ptr)
    {
        cout << "this is someOtherType"<<endl;
    }
    }
};

int main() {
    
    Animal *pig = new Pig();
    Dog  *dog = new Dog();
    pig->animalSound();
    dog->animalSound();
    pig->printSpeed();
    dog->printSpeed();
    dog->writeToFIle("myFile.txt", "text");
    dog->readFromFile("myFile1.txt");
    return 0;
}