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
    int priority; // Lower number => higher priority for RMS, if you wish
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

// Function to check if all jobs are completed
bool allJobsCompleted(const vector<Job>& jobs)
{
    for (const auto& job : jobs) {
        if (job.remainingTime > 0) {
            return false;
        }
    }
    return true;
}

// Function to find the job with the highest priority
Job *highest_priority(vector<Job *>& readyList)
{
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

int main(int argc, char* argv[])
{
    if (argc != 2) {
        cerr << "Usage: " << argv[0] << " <tasks.csv>" << endl;
        return 1;
    }

    string filename = argv[1];
    vector<Task> tasks;
    readTasksCSV(filename, tasks);

    int n = 1000; 
    int currentTime = 0;

    vector<Job> jobs;
    jobs.reserve(tasks.size());
    for (const auto& t : tasks) {
        jobs.push_back({t, 0, t.WCET, 0});
    }

    vector<int> worstCaseResponseTimes(tasks.size(), 0);

    while (currentTime < n && !allJobsCompleted(jobs))
    {
        // Release new jobs at the start of each period
        for (const auto& t : tasks) 
        {
            if (currentTime != 0 && currentTime % t.period == 0) {
                jobs.push_back({t, currentTime, t.WCET, 0});
            }
        }

        // Get the list of ready jobs
        vector<Job*> readyList = get_ready(jobs, currentTime);

        // If no jobs are ready, increment the current time
        if (readyList.empty()) 
        {
            currentTime++;
            continue;
        }

        // Get the job with the highest priority
        Job* currentJob = highest_priority(readyList);

        if (currentJob != nullptr)
        {
            // Execute the job for one time unit
            currentJob->remainingTime--;
            currentTime++;
    
            // If the job is completed, update its response time
            if (currentJob->remainingTime <= 0) 
            {
                currentJob->responseTime = currentTime - currentJob->releaseTime;
                int taskIndex = distance(
                    tasks.begin(),
                    find_if(tasks.begin(), tasks.end(), [&](const Task& tk){
                        return tk.id == currentJob->task.id;
                    })
                );
                worstCaseResponseTimes[taskIndex] = max(
                    worstCaseResponseTimes[taskIndex],
                    currentJob->responseTime
                );
            }
        }
        else
        {
            currentJob->remainingTime--;
            currentTime++;
        }
    }

    // Output the worst-case response times for each task
    for (size_t i = 0; i < tasks.size(); ++i) 
    {
        cout << "Task " << tasks[i].id
             << " WCRT: " << worstCaseResponseTimes[i] << endl;
    }

    return 0;
}