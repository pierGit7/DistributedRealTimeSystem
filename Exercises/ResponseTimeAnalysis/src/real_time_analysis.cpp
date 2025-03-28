#include <iostream>
#include <vector>
#include <algorithm>
#include <fstream>
#include <sstream>
#include <cmath>

using namespace std;

struct Task {
    string id;
    int BCET;
    int WCET;
    int period;  
    int deadline; 
    int priority; // Lower number => higher priority for RMS, if you wish
};


void readTasksCSV(const string& filename, vector<Task>& tasks)
{
    ifstream file(filename);
    if (!file.is_open()) {
        cerr << "Error: Could not open file " << filename << endl;
        return;
    }

    string line;
    getline(file, line); // Skip header

    while (getline(file, line))
    {
        stringstream ss(line);
        Task task;
        string token;

        getline(ss, token, ','); // Task ID
        task.id = token;
        getline(ss, token, ','); // WCET
        task.WCET = stoi(token);
        getline(ss, token, ','); // BCET
        task.BCET = stoi(token);
        getline(ss, token, ','); // Period
        task.period = stoi(token);
        getline(ss, token, ','); // Deadline
        task.deadline = stoi(token);
        getline(ss, token, ','); // Priority
        task.priority = stoi(token);

        tasks.push_back(task);
    }
    file.close();
}

void RTA_test(vector<Task>& tasks)
{
    // Sort tasks by priority (lower number means higher priority)
    sort(tasks.begin(), tasks.end(), [](const Task& a, const Task& b) {
        return a.priority < b.priority;  // Ensure lower priority number = higher priority
    });

    for (size_t task = 0; task < tasks.size(); task++)
    {
        int R = tasks[task].WCET;
        int last_R = -1;
        bool schedulable = true;
        int I = 0; // Reset interference for each iteration

        while (R != last_R)
        {
            last_R = R;

            // Compute interference from higher-priority tasks
            for (size_t j = 0; j < task; j++)
            {
                I += ceil((double)R / tasks[j].period) * tasks[j].WCET;
            }

            R = I + tasks[task].WCET;

            if (R > tasks[task].deadline)
            {
                cout << "Task " << tasks[task].id << " is not schedulable." << endl;
                schedulable = false;
                break;
            }
        }

        if (schedulable)
        {
            cout << "Task " << tasks[task].id << " is schedulable with WCRT = " << R << endl;
        }
    }
}

int main(int argc, char* argv[])
{
    if (argc != 2) {
        cerr << "Usage: " << argv[0] << " <tasks.csv>" << endl;
        return 1;
    }

    string filename = argv[1];
    vector<Task> tasks;
    readTasksCSV(filename, tasks);

    RTA_test(tasks);

    return 0;
}