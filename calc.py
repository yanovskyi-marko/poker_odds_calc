import random as r
import itertools as iter

points_for_flush=10
points_for_straight=9

color_dict={"\u1F0A","\u1F0B", "\u1F0C", "\u1F0D"}
colors = ["Clubs","Diamonds","Hearts","Spades"]
numbers = [i for i in range(13)]
cards = [(i,j) for i in numbers for j in colors]



def get_numbers(hand):
    return [i for i,_ in hand]

def get_colors(hand):
    return [j for _,j in hand]


# Creates a dictionary of (card number : number repetitions) or if it's colors (color : number of repetitions)
def get_dict_duplicates(card_signs):
    duplics = dict()
    for i in card_signs:
        if i in duplics:
            duplics[i]+=1
        else:
            duplics[i]=1
    return duplics 
# gets the repetitions list from card numbers or from card colros example get_list_of_duplicates(get_colors( [(1,"Clubls"), (2,"Clubls"),(2,"Spades"),(2,"Hearts"), (2,"Diamonds")])) gives this -> [2,1,1,1]

def get_list_of_duplicates(card_signs):
    return [i for _,i in get_dict_duplicates(card_signs).items()]
# calculates the series of cards for example suites( [(1,"Clubls"), (2,"Clubls"),(3,"Spades"),(2,"Hearts"), (2,"Diamonds")]) gives this -> [3,1,1]
def suites(hand):
    hand = sorted (hand)
    k=1
    l=[]
    for i in range(len(hand)-1):
        if hand[i]+1==hand[i+1]:
            k+=1
        else:
            l.append(k)
            k=1
    l.append(k)
    return l 

#calculates points from duplicates just by multiplying (the number of repetitions +1) with (the number of repetitions -1)
#that gives us these points:
#pair - 3
#two pairs - 6
#three of a kind - 8
#full house - 11
#four of a kind - 15

def points_from_duplicates(duplicates):
    return sum([(i+1)*(i-1) for i in duplicates])

#we also know that flush is between three of a kind and full house, but higher then straight so we give 10 points for it
def points_from_flush(same_color_cards):
    return points_for_flush if len(same_color_cards)==1 else 0
#and at last we know that straight is between three of a kind and full house, but lower then flush so we give 9 points for it
def points_from_straight(suite):
    return points_for_straight if len(suite) ==1 else 0


# to calculate the points for the highest cards we take into account that we first need to compare the cards of the highest rank, then if they are equal we pass to the following rank and so on.
# a way to do it is to transform it into one number between 0 and 1. to do it we need to devide everything by 13 then each card from the list [c1,c2,c3,c4,c5] we add but each following card should be one order of magnitude bigger then the previous to make it more significant. example:
#[1,2,2,4,11] here we transform cards into this list [1,4,11,4]  
#[1,4,2,2,11] here we transform cards into this list [1,4,11,4]
#[1,1,2,2,11] here we transform cards into this list [11,2,4]
# and then taking as an example the first list we multiply everything and add up (1*(3**2)+4*(3**3)+11*(3**4)+4*(3**5))/(13*(3**4)*5)
#formula is:
#for i in range(5-len(hand), 5):
#    sum+=hand[(5-(len(hand))-i)]*((x)**i)
# here the difficulty was with calculating a good multiplier(x to the power of i) for each card so that when I add them up four of 12's + some other card it would be bigger then the sum of four of 11's and any other card. The difficulty was actually in coming up with such a solution rather then solving the equation; In the end I just translated what I said above into an equation (4*12*(x**4))+1*(x**3)>4*11*(x**4)+11*(x**3) which solves to x>3 (rougly)

#side note one can take any arbitrary large number but one should be aware of floating point conveting
def points_from_highest_card(hand):
    d = get_dict_duplicates(get_numbers(hand))
    sum=0
    hand=[i*k for i,k in sorted(d.items(), key=lambda p : p[0]+12*p[1])] # you can't change k here cuz the calculations above break

    for i in range(5-len(hand), 5):
        sum+=hand[(5-(len(hand))-i)]*((3)**i) # x to the power of i multiplier
    return (sum/(13*(3**4)*5))
#to calculate points we just add all points together
def total_points_hand(hand):
    dc = get_list_of_duplicates(get_colors(hand))
    dn = get_list_of_duplicates(get_numbers(hand))
    s = suites(get_numbers(hand))
    total = points_from_flush(dc)+points_from_duplicates(dn)+points_from_straight(s)+points_from_highest_card(hand)
    return total





#FUN PART 
#--------------------------------------------------------------------------------------------------
#calculating probabilities of winning
#
#
#
#
def calculate_the_winning_with_7_cards_in_the_pool(pool,visible_cards,not_visible_cards):

    #Step one: calculate a list of all possible hands that you can get from your hand and the pool 
    your_possible_hands = [list(i) for i in iter.combinations(visible_cards, 5)]

    #Step two: calculate the best hand among those
    best_hand = max(your_possible_hands, key=lambda p : total_points_hand(p))
    total_points_from_best_hand=total_points_hand(best_hand)

    #Step three : calculate a list of all possible hands that your opponents can have
    opponent_visible_cards = [list(i)+pool for i in iter.combinations(not_visible_cards, 2)]
    opponent_possible_hands= []
    for k in opponent_visible_cards:
        opponent_possible_hands.append( max([list(i) for i in iter.combinations(k, 5)], key=lambda p : total_points_hand(p))) 
    # here I had a bug where I didn't use the max function to find the best hand from all possible hands that my opponent can have(it's the best hand from seven cards) instead I just added all possible hands into opponent_possible_hands list and then it made my probabilities way to low

    #Step four : filter the cards that are the better then yours

    better_hands = list(filter(lambda p : total_points_hand(p)>total_points_from_best_hand, opponent_possible_hands))


    #Step five : calculate the ratio of all possible hands that are better that your opponent can have devided by all possible hands that your opponent can have
    probability_of_loosing = len(better_hands)/len(opponent_possible_hands)
    # calculating every possible hand in the game
    return probability_of_loosing

def calculate_the_winning_with_the_nth_card_in_the_pool(pool,your_hand):
    visible_cards=your_hand+pool
    not_visible_cards=[i for i in cards if i not in visible_cards]
    possible_pools = [list(i)+pool for i in iter.combinations(not_visible_cards, 5-len(pool))]
    probability_of_loosing=0;
    for p in possible_pools:
        probability_of_loosing+=calculate_the_winning_with_7_cards_in_the_pool(p, visible_cards,not_visible_cards)
    return not_visible_cards, probability_of_loosing/len(possible_pools)

#devide cards into three piles the first that is your hand of two cards, the second is the pool and the third that is not visible to you 

first_div= r.sample(cards, k=5)
pool = r.sample(first_div, k=3)
your_hand = [i for i in first_div if i not in pool]

#pool= [(10, 'Spades'), (10, 'Clubs'), (4, 'Spades'), (10, 'Diamonds'), (10, 'Hearts')]
#your_hand = [(0,"Spades"),(1,"Clubs")]   
for i in range(1,4):
    not_visible_cards, probability_of_loosing = calculate_the_winning_with_the_nth_card_in_the_pool(pool, your_hand)
    print(str(i)+"th card in the pool")
    print("pool is :"+str(pool))
    print("your hand is :"+str(your_hand))
    print("probability that your opponent will win is: " + str(probability_of_loosing))
    pool.append(r.choice(not_visible_cards))

all_possible_hands= iter.combinations(cards, 5)


