#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <map>
#include <algorithm>
#include <ctime>
#include <set>

using namespace std;

// Map of user IDs to names
map<string, string> userIdToName = {
    {"737083415", "Misha"},
    {"569684117", "Yulia"},
    {"428077041", "Kolia"},
};

// Базовий клас
class UserAction {
public:
    string timestamp;
    string userID;

    UserAction(const string& timestamp, const string& userID)
        : timestamp(timestamp), userID(userID) {}

    virtual void print() const = 0; // Pure virtual function makes this class abstract
};

// Derived class
class CommandAction : public UserAction {
public:
    string command;

    CommandAction(const string& timestamp, const string& userID, const string& command)
        : UserAction(timestamp, userID), command(command) {}

    void print() const override {
        string userName = userIdToName[userID];
        cout << "User " << userName << " issued command " << command << " at " << timestamp << "\n";
    }
};

// Now, instead of a vector of UserAction structs, you'll have a vector of pointers to UserAction objects
vector<UserAction*> readUserActions(const string& filename) {
    vector<UserAction*> userActions;
    ifstream file(filename);
    string line;

    while (getline(file, line)) {
        istringstream iss(line);
        string timestamp, userID, command;

        getline(iss, timestamp, ' ');
        iss.ignore(numeric_limits<streamsize>::max(), ' ');
        iss.ignore(numeric_limits<streamsize>::max(), ' ');
        iss.ignore(numeric_limits<streamsize>::max(), ' ');
        iss.ignore(numeric_limits<streamsize>::max(), ' ');
        iss.ignore(numeric_limits<streamsize>::max(), ' ');
        getline(iss, userID, ' ');
        iss.ignore(numeric_limits<streamsize>::max(), ' ');
        iss.ignore(numeric_limits<streamsize>::max(), ' ');
        getline(iss, command);

        userActions.push_back(new CommandAction(timestamp, userID, command));
    }

    return userActions;
}

map<string, int> countCommandsPerUser(const vector<UserAction*>& actions) {
    map<string, int> commandCounts;

    for (const auto& action : actions) {
        commandCounts[action->userID]++;
    }

    return commandCounts;
}

string findMostFrequentCommand(const vector<UserAction*>& actions) {
    map<string, int> commandCounts;

    for (const auto& action : actions) {
        CommandAction* commandAction = dynamic_cast<CommandAction*>(action);
        if (commandAction) {
            commandCounts[commandAction->command]++;
        }
    }

    if (commandCounts.empty()) {
        return ""; // or some other appropriate value
    }

    return max_element(commandCounts.begin(), commandCounts.end(),
        [](const auto& a, const auto& b) {
            return a.second < b.second;
        })->first;
}

int countCommandUsage(const vector<UserAction*>& actions, const string& command) {
    int count = 0;

    for (const auto& action : actions) {
        CommandAction* commandAction = dynamic_cast<CommandAction*>(action);
        if (commandAction && commandAction->command.find(command) != string::npos) {
            count++;
        }
    }

    return count;
}


pair<string, int> findUserMostFrequentCommand(const vector<UserAction*>& actions) {
    map<string, map<string, int>> userCommandCounts;

    for (const auto& action : actions) {
        CommandAction* commandAction = dynamic_cast<CommandAction*>(action);
        if (commandAction) {
            userCommandCounts[action->userID][commandAction->command]++;
        }
    }

    string topUser;
    string topCommand;
    int topCount = 0;

    for (const auto& [user, commands] : userCommandCounts) {
        for (const auto& [command, count] : commands) {
            if (count > topCount) {
                topUser = user;
                topCommand = command;
                topCount = count;
            }
        }
    }

    return { topUser, topCount };
}

void printLine() {
    cout << "\t\t -------------------------------------------------------------------------\n";
}

void printStartMessage() {
    printLine();
    cout << "\t\t|\t\t\t\t  Привіт! \t\t\t\t  |\n ";
    cout << "\t\t|                  Ви перебуваєте у меню для статистики                   |\n";
    cout << "\t\t|   тут можна дізнатись багато цікавої інформації про учасників кімнати   |\n";
    cout << "\t\t|       хто є найбільш відповідальним, найбільш лінивим і всяке інше      |\n";
    printLine();
}

void printMenu() {
    cout << endl;
    printLine();
    cout << "\t\t|\t\t\t    Функціонал програми      \t\t\t  |\n";
    cout << "\t\t|           (цифра в дужках показує номер команди для виклику)\t\t  |\n";
    cout << "\t\t|\t\t\t\t\t\t\t\t\t  |\n";
    cout << "\t\t| (-1) Завершити виконання програми                                       |\n";
    cout << "\t\t|  (0) Вивести функціонал програми ще раз                                 |\n";
    cout << "\t\t|  (1) Дізнатись яку команду вживали найбільш часто(з вибором проміжку)   |\n";
    cout << "\t\t|  (2) Вивести ТОП-5 найбільш вживаних команд чату                        |\n";
    cout << "\t\t|  (3) ТОП-5 користувачів, які найчастіше використовують певну команду    |\n";
    cout << "\t\t|  (4) Користувач, який найчастіше додавав товари для покупки             |\n";
    cout << "\t\t|  (5) Користувач, який найчастіше підтверджує покупки                    |\n";
    cout << "\t\t|  (6) Користувач, який найчастіше перевіряє список покупок               |\n";
    cout << "\t\t|  (7) Користувач, який найчастіше мінявся під час прибирання             |\n";
    cout << "\t\t|  (8) Користувач, який найбільше пропускав свою чергу для прибирання     |\n";
    cout << "\t\t|  (9) Користувач, який вважається найбільш відповідальним                |\n";
    cout << "\t\t| (10) Користувач, який частіше за інших хвилюється за кількістю води     |\n";
    cout << "\t\t| (11) Користувач, який найчастіше використовує функцію свапу за водою    |\n";
    cout << "\t\t| (12) Користувач, який використовує найбільшу кількість унікальних команд|\n";
    cout << "\t\t| (13) Користувач, якому найбільше цікаво чия черга прибирати             |\n";
    cout << "\t\t| (14) Користувач, якому найбільше цікаво чия черга йти по воду           |\n";
    printLine();
}


void printFunctionality() {
    printMenu();
}

void mostFrequentCommand(const vector<UserAction*>& actions, const string& startTime, const string& endTime) {
    map<string, int> commandCounts;

    for (const auto& action : actions) {
        CommandAction* commandAction = dynamic_cast<CommandAction*>(action);
        // Перевірте, чи час дії входить у вказаний проміжок часу
        if (commandAction && commandAction->timestamp >= startTime && commandAction->timestamp <= endTime) {
            commandCounts[commandAction->command]++;
        }
    }

    if (commandCounts.empty()) {
        cout << "Немає команд, які були використані в цей проміжок часу.\n";
        return;
    }

    auto maxIt = max_element(commandCounts.begin(), commandCounts.end(), [](const auto& a, const auto& b) {
        return a.second < b.second;
        });

    cout << "Найбільш часто використана команда в цей проміжок часу: " << maxIt->first << " (" << maxIt->second << " раз)\n";
}

void top5Commands(const vector<UserAction*>& actions) {
    map<string, int> commandCounts;

    for (const auto& action : actions) {
        CommandAction* commandAction = dynamic_cast<CommandAction*>(action);
        if (commandAction) {
            commandCounts[commandAction->command]++;
        }
    }

    vector<pair<string, int>> commandCountsVec(commandCounts.begin(), commandCounts.end());
    sort(commandCountsVec.begin(), commandCountsVec.end(), [](const auto& a, const auto& b) {
        return a.second > b.second;
        });

    cout << "ТОП-5 найбільш вживаних команд:\n";
    for (int i = 0; i < min(5, (int)commandCountsVec.size()); i++) {
        cout << i + 1 << ". " << commandCountsVec[i].first << " (" << commandCountsVec[i].second << " раз)\n";
    }
}

void top5UsersForCommand(const vector<UserAction*>& actions, const string& command) {
    map<string, int> userCounts;

    for (const auto& action : actions) {
        CommandAction* commandAction = dynamic_cast<CommandAction*>(action);
        if (commandAction && commandAction->command == command) {
            userCounts[action->userID]++;
        }
    }

    vector<pair<string, int>> userCountsVec(userCounts.begin(), userCounts.end());
    sort(userCountsVec.begin(), userCountsVec.end(), [](const auto& a, const auto& b) {
        return a.second > b.second;
        });

    cout << "ТОП-5 користувачів, які найчастіше використовують команду " << command << ":\n";
    for (int i = 0; i < min(5, (int)userCountsVec.size()); i++) {
        string userName = userIdToName[userCountsVec[i].first];
        cout << i + 1 << ". " << userName << " (" << userCountsVec[i].second << " раз)\n";
    }
}

void mostFrequentAdder(const vector<UserAction*>& actions) {
    map<string, int> userCounts;

    for (const auto& action : actions) {
        CommandAction* commandAction = dynamic_cast<CommandAction*>(action);
        if (commandAction && commandAction->command == "/add") {
            userCounts[action->userID]++;
        }
    }

    if (userCounts.empty()) {
        cout << "Немає користувачів, які додавали товари.\n";
        return;
    }

    auto maxIt = max_element(userCounts.begin(), userCounts.end(), [](const auto& a, const auto& b) {
        return a.second < b.second;
        });

    string userName = userIdToName[maxIt->first];
    cout << "Користувач, який найчастіше додавав товари: " << userName << " (" << maxIt->second << " раз)\n";
}

pair<string, int> findUserMostFrequentCommandForSpecificAction(const vector<UserAction*>& actions, const string& specificCommand) {
    map<string, int> userCommandCounts;

    for (const auto& action : actions) {
        CommandAction* commandAction = dynamic_cast<CommandAction*>(action);
        if (commandAction && commandAction->command == specificCommand) {
            userCommandCounts[action->userID]++;
        }
    }

    string topUser;
    int topCount = 0;

    for (const auto& [user, count] : userCommandCounts) {
        if (count > topCount) {
            topUser = user;
            topCount = count;
        }
    }

    return { topUser, topCount };
}


void mostFrequentConfirmer(const vector<UserAction*>& actions) {
    string command = "/del";
    auto [user, count] = findUserMostFrequentCommandForSpecificAction(actions, command);
    string userName = userIdToName[user];
    cout << "User " << userName << " confirmed purchases the most with " << count << " times\n";
}

void mostFrequentListChecker(const vector<UserAction*>& actions) {
    string command = "/list";
    auto [user, count] = findUserMostFrequentCommandForSpecificAction(actions, command);
    string userName = userIdToName[user];
    cout << "User " << userName << " checked the list the most with " << count << " times\n";
}

void mostFrequentSwapper(const vector<UserAction*>& actions) {
    string command = "/swap";
    auto [user, count] = findUserMostFrequentCommandForSpecificAction(actions, command);
    string userName = userIdToName[user];
    cout << "User " << userName << " swapped the most with " << count << " times\n";
}

void mostFrequentSkipper(const vector<UserAction*>& actions) {
    auto [userID, count] = findUserMostFrequentCommandForSpecificAction(actions, "skip");
    string userName = userIdToName[userID];
    cout << "Користувач " << userName << " найчастіше пропускав свою чергу для прибирання, зробивши це " << count << " разів\n";
}

void mostResponsibleUser(const vector<UserAction*>& actions) {
    auto [userID, count] = findUserMostFrequentCommandForSpecificAction(actions, "confirm");
    string userName = userIdToName[userID];
    cout << "Користувач " << userName << " вважається найбільш відповідальним, підтвердивши прибирання " << count << " разів\n";
}

void mostFrequentWaterWorrier(const vector<UserAction*>& actions) {
    auto [userID, count] = findUserMostFrequentCommandForSpecificAction(actions, "wstart");
    string userName = userIdToName[userID];
    cout << "Користувач " << userName << " частіше за інших хвилюється за кількістю води, зробивши запит " << count << " разів\n";
}

void mostFrequentWaterSwapper(const vector<UserAction*>& actions) {
    auto [userID, count] = findUserMostFrequentCommandForSpecificAction(actions, "wswap");
    string userName = userIdToName[userID];
    cout << "Користувач " << userName << " найчастіше використовує функцію свапу за водою, виконавши це " << count << " разів\n";
}

void mostUniqueCommands(const vector<UserAction*>& actions) {
    map<string, set<string>> userUniqueCommands;
    for (const auto& action : actions) {
        CommandAction* commandAction = dynamic_cast<CommandAction*>(action);
        if (commandAction) {
            userUniqueCommands[action->userID].insert(commandAction->command);
        }
    }

    string topUser;
    int topCount = 0;

    for (const auto& [user, commands] : userUniqueCommands) {
        if (commands.size() > topCount) {
            topUser = user;
            topCount = commands.size();
        }
    }

    string userName = userIdToName[topUser];
    cout << "Користувач " << userName << " використовує найбільшу кількість унікальних команд, використовуючи " << topCount << " унікальних команд\n";
}


void mostInterestedInCleaning(const vector<UserAction*>& actions) {
    auto [userID, count] = findUserMostFrequentCommandForSpecificAction(actions, "qlist");
    string userName = userIdToName[userID];
    cout << "Користувач " << userName << " найбільше цікавиться, чия черга прибирати, перевіривши це " << count << " разів\n";
}

void mostInterestedInWater(const vector<UserAction*>& actions) {
    auto [userID, count] = findUserMostFrequentCommandForSpecificAction(actions, "wlist");
    string userName = userIdToName[userID];
    cout << "Користувач " << userName << " найбільше цікавиться, чия черга йти по воду, перевіривши це " << count << " разів\n";
}


void getUserOption() {
    int ch = 0;
    string command;
    string startTime, endTime;
    printStartMessage();
    printMenu();
    vector<UserAction*> actions = readUserActions("user_actions.log");
    while (true) {
        cin >> ch;
        if (cin.fail()) {
            cin.clear(); //clear input buffer to restore cin to a usable state
            cin.ignore(INT_MAX, '\n'); //ignore last input
            cout << "You've entered wrong input. Please, enter a number." << endl;
            continue;
        }
        if (ch == -1) {
            break;
        }
        switch (ch)
        {
        case 0:
            printFunctionality();
            break;
        case 1:
            cout << "Введіть початковий час у форматі YYYY-MM-DD: ";
            cin >> startTime;
            getchar();
            cout << "Введіть кінцевий час у форматі YYYY-MM-DD: ";
            cin >> endTime;
            mostFrequentCommand(actions, startTime, endTime);
            break;
        case 2:
            top5Commands(actions);
            break;
        case 3:
            cout << "Enter the command for which you want to find the top 5 users: ";
            cin >> command;
            top5UsersForCommand(actions, command);
            break;
        case 4:
            mostFrequentAdder(actions);
            break;
        case 5:
            mostFrequentConfirmer(actions);
            break;
        case 6:
            mostFrequentListChecker(actions);
            break;
        case 7:
            mostFrequentSwapper(actions);
            break;
        case 8:
            mostFrequentSkipper(actions);
            break;
        case 9:
            mostResponsibleUser(actions);
            break;
        case 10:
            mostFrequentWaterWorrier(actions);
            break;
        case 11:
            mostFrequentWaterSwapper(actions);
            break;
        case 12:
            mostUniqueCommands(actions);
            break;
        case 13:
            mostInterestedInCleaning(actions);
            break;
        case 14:
            mostInterestedInWater(actions);
            break;
        default:
            cout << "Invalid input, try one more time " << endl;
            break;
        }
    }
}

int main() {
    system("chcp 1251");
    system("cls");
    getUserOption();
    return 0;
}