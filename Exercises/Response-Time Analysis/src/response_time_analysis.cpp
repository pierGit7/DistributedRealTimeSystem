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
        getline(ss, token, ','); // BCET
        task.BCET = stoi(token);
        getline(ss, token, ','); // WCET
        task.WCET = stoi(token);
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
        return a.priority < b.priority;
    });

    for (size_t i = 0; i < tasks.size(); i++)
    {
        int R = tasks[i].WCET;
        int last_R = -1;
        bool schedulable = true;

        while (R != last_R)
        {
            last_R = R;
            int I = 0;
            for (size_t j = 0; j < i; j++)
            {
                I += ceil((double)R / tasks[j].period) * tasks[j].WCET;
            }
            R = tasks[i].WCET + I;

            if (R > tasks[i].deadline)
            {
                cout << "Task " << tasks[i].id << " is not schedulable with WCRT." << endl;
                schedulable = false;
                break;
            }
        }

        if (schedulable)
        {
            cout << "Task " << tasks[i].id << " is schedulable with WCRT = " << R << endl;
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
