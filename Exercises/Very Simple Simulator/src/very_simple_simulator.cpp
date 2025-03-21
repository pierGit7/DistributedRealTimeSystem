#include <iostream>
#include <vector>
#include <algorithm>
#include <fstream>
#include <sstream>

using namespace std;

// Define the Task structure
struct Task {
    string id;
    int BCET;
    int WCET;
    int period;  
    int deadline; 
    int priority; // Lower number => higher priority for RMS
};

// Define the Job structure
struct Job {
    Task task;
    int releaseTime;
    int remainingTime;
    int responseTime;
};

// Function to read tasks from a CSV file
void readTasksCSV(const string& filename, vector<Task>& tasks)
{
    ifstream file(filename);
    if (!file.is_open()) 
    {
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

    sort(tasks.begin(), tasks.end(), [](const Task& a, const Task& b) {
        return a.id < b.id;
    });
}

// Function to find the job with the highest priority
Job *highest_priority(vector<Job *>& readyList)
{
    if (readyList.empty()) 
    {
        return nullptr;
    }

    return *min_element(
        readyList.begin(),
        readyList.end(),
        [](Job* a, Job* b) {
            return a->task.priority < b->task.priority; 
        }
    );
}

// Function to get the list of ready jobs
vector<Job*> get_ready(vector<Job>& jobs, int currentTime)
{
    vector<Job*> readyList;
    for (auto& j : jobs) {
        if (j.releaseTime <= currentTime && j.remainingTime > 0) {
            readyList.push_back(&j);
        }
    }
    return readyList;
}

int advanceTime()
{
    return 1;
}

int main(int argc, char* argv[])
{
    if (argc != 2) 
    {
        cerr << "Usage: " << argv[0] << " <tasks.csv>" << endl;
        return 1;
    }

    string filename = argv[1];
    vector<Task> tasks;
    readTasksCSV(filename, tasks);

    // Simulation time (n cycles)
    int n = 1000; 
    int currentTime = 0;

    // List of all jobs that are in the system
    vector<Job> jobs;

    // Initialize next release time for each task (all tasks start at time 0)
    vector<int> nextReleaseTimes(tasks.size(), 0);

    // We also maintain worst-case response times (WCRT) for each task.
    vector<int> worstCaseResponseTimes(tasks.size(), 0);

    // Simulation loop
    while (currentTime <= n)
    {
        // For each task, if it is time to release a new job, create it.
        for (size_t i = 0; i < tasks.size(); ++i) 
        {
            if (currentTime >= nextReleaseTimes[i]) 
            {
                Job newJob { tasks[i], currentTime, tasks[i].WCET, 0 };
                jobs.push_back(newJob);
                nextReleaseTimes[i] += tasks[i].period;
            }
        }
        
        vector<Job*> readyList = get_ready(jobs, currentTime);
        Job* currentJob = highest_priority(readyList);

        if (currentJob != nullptr)
        {
            int delta = advanceTime();
            currentTime += delta;
            currentJob->remainingTime -= delta;

            // If the job has completed execution, calculate its response time and update WCRT
            if (currentJob->remainingTime <= 0) 
            {
                currentJob->responseTime = currentTime - currentJob->releaseTime;
                
                // Find the corresponding task index
                auto it = find_if(tasks.begin(), tasks.end(), [&](const Task& t) {
                    return t.id == currentJob->task.id;
                });

                if (it != tasks.end()) 
                {
                    size_t taskIndex = distance(tasks.begin(), it);
                    worstCaseResponseTimes[taskIndex] = max(
                        worstCaseResponseTimes[taskIndex],
                        currentJob->responseTime
                    );
                }
            }
        }
        else
        {
            // If no job is ready, just advance time
            int delta = advanceTime();
            currentTime += delta;
        }
    }

    // Output the worst-case response times for each task
    cout << "Task\tWCRT\tDeadline\tStatus" << endl;
    cout << "---------------------------------" << endl;
    for (size_t i = 0; i < tasks.size(); ++i) 
    {
        string status = (worstCaseResponseTimes[i] <= tasks[i].deadline) ? "✓" : "✗";
        cout << " " << tasks[i].id << "\t" 
            << worstCaseResponseTimes[i] << "\t" 
            << tasks[i].deadline << "\t\t" 
            << status << endl;
    }

    return 0;
}
