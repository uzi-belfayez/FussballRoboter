import matplotlib.pyplot as plt
from IPython import display

plt.ion()

def plot(scores, mean_scores):
    display.clear_output(wait=True)
    plt.figure(1)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Training...')
    plt.xlabel('Number of Games')
    plt.ylabel('Score')
    plt.plot(scores)
    plt.plot(mean_scores)
    plt.ylim(ymin=0)
    plt.text(len(scores)-1, scores[-1], str(scores[-1]))
    plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1]))
    plt.show(block=False)
    plt.pause(.1)

def plot_rewards(positive_rewards, negative_rewards):
    display.clear_output(wait=True)
    plt.figure(2)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Rewards...')
    plt.xlabel('Number of Games')
    plt.ylabel('Score')
    plt.plot(positive_rewards)
    plt.plot(negative_rewards)

    plt.text(len(positive_rewards)-1, positive_rewards[-1], str(positive_rewards[-1]))
    plt.text(len(negative_rewards)-1, negative_rewards[-1], str(negative_rewards[-1]))
    plt.show(block=False)
    plt.pause(.1)