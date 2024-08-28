import tilearn

x = [['French homework', 6, 3, 6, 8], ['Maths homework', 6, 3, 6, 8], ['IELTS practice', 2, 1, 6, 3], ['Review Maths', 3, 5, 4, 7], ['Study French', 3, 6, 3, 7], ['Housework', 3, 5, 4, 7], ['Coding practice', 2, 1, 6, 3], ['Reading book', 10, 3, 6, 8], ['Piano lesson', 3, 6, 3, 7], ['English homework', 3, 6, 3, 7]]

# print(tilearn.show_mytime(x, 30))

scheduling = tilearn.show_mytime(x, 30)

for row in scheduling:
    print(row)