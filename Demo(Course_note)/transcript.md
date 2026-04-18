# How Reasoning LLMs Like GPT-5 Are Built
## Introduction to Reasoning

0:00

In this video, we'll look at reasoning

0:01

LLMs, which power many of today's most

0:04

advanced chatbots like GPT5.

0:06

We will cover three things. One, what

0:09

reasoning LLM are. Two, different

0:12

inference time and training time

0:13

techniques to build reasoning LLMs.

0:16

And three, what the GPT5 unified system

0:19

might look like.

0:22

A short background here. After the

0:24

success of a standard LLMs like GPT3 and

0:26

GPT4, Lama family and Gemini between 22

0:30

and 24, open released 01 model in

0:34

September 24 and framed it as a model

0:36

that can think.

0:39

Also in this article, they are

0:41

introducing open as a new series of AI

0:44

models designed to spend more time

0:46

thinking before they respond.

0:49

They also published another article on

0:51

the same day and this artic art article

0:53

is mostly focused on the evaluation and

0:55

they are showing that how much

0:56

improvements they are getting by

0:58

training this reasoning LLM. If we

1:01

scroll to the eval part we will see on

1:03

different benchmarks for example Amy

1:05

which contains USA math olympiad

1:07

questions 01 models are doing

1:10

significantly better than the

1:12

non-reasoning equivalent which was GPT40

1:15

back then. And this line is showing the

1:17

accuracy of these models. And similarly,

1:20

they're showing on other benchmarks like

1:22

competition code, code code forces

1:23

benchmark or PhD level science

1:25

questions, 01 is doing a lot better than

1:27

GPT40.

1:31

After that, we observed a wave of

1:33

reasoning models from different teams

1:35

and companies. Popular examples are um

1:38

CL, Gemini 2.5 Pro, GPT5, Deepsec R1 and

1:42

there are a lot more examples. And most

1:45

of these reasoning models are released

1:46

in 25.

1:50

I think this meme nicely visualizes what

1:52

we just saw. In 24 we had all these

1:55

non-reasoning um LLMs and then 01 came

1:58

and now we have in 25 we have a lot more

2:01

u powerful reasoning models being

2:04

released and introduced and many of

2:06

these are doing very good on different

2:07

benchmarks.

2:09

So next let's see what reasoning LLM

2:12

are.

2:14

What is reasoning? If we go to Wikipedia

2:18

and search for reason, we would see in a

2:20

great detail what reasoning is. Uh

2:21

different definitions in cognitive

2:23

psychology and others other domains. We

2:26

would also see different forms of

2:27

reasoning. So if you are interested, you

2:29

can read this page. It's it's quite

2:31

long.

2:32

But the summary is in cognitive

2:34

psychology, the definition of reasoning

2:36

is the process of drawing conclusions

2:38

based on available information. And

2:41

reasoning can also appear in different

2:43

forms. For example, we have common sense

2:45

reasoning where questions like do people

2:48

wear sunglasses requires that. We have

2:51

mathematical reasoning where the

2:52

question is just a math problem and then

2:54

it requires some multi multi-step

2:56

reasoning to answer it. We have also

2:59

other forms of reasoning like multihub

3:00

reasoning, um logical reasoning, abduct

3:03

abductive reasoning and so on. So this

3:06

is the definition of reasoning. Now the

3:09

next question is can LLM reason and

3:12

there is a lot of argument between

3:14

different people whether LLMs can truly

3:16

reason or not but what is important is

3:19

how we define def how we define

3:21

reasoning in LLMs and in AI and I think

3:24

a very great definition of reasoning

3:27

comes from Denny um and Denny is

3:29

basically founded and lead the reasoning

3:32

team in Google brain and now part of

3:33

Google deep mind and in one of his talks

3:36

he defines

3:38

reasoning in LLMs as the presence of

3:40

intermediate tokens between question and

3:42

final answer. So for example in a

3:45

non-reasoning setup we have this LLM the

3:47

problem goes here and then the final

3:49

answer is out

3:52

whereas in a reasoning LLM it still the

3:55

problem goes into the LLM but the LLM

3:57

first generates some intermediate tokens

4:00

and after that it generates the final

4:02

answer. So basically we are going from

4:04

this quick single pass in non-reasoning

4:06

LLMs to a sequence of intermediate steps

4:09

followed by the final answer in

4:11

reasoning LLMs. Now to see a concrete

4:14

example of these intermediate tokens.

4:16

Let's go to hyperbolic. Hyperbolic is a

4:19

platform which allows you to use

4:21

different open source models and run

4:23

inference meaning that you send some

4:26

questions and get some answers. And

4:28

there are also other u providers. I just

4:30

use hyperbolic. And then here there are

4:32

a bunch of different models we can

4:34

choose. Um for example GPT OSS is the

4:37

open AAI's open weight model and there

4:39

are a bunch of other models like Quinn

4:40

and Kim K2 and so on. So here um I would

4:45

first select a non-reasoning model and

4:48

ask a question like a difficult question

4:50

like um I just learned AI and it sounds

4:56

fun.

4:59

How can I

5:02

win a touring award

5:08

in one year? So now this lamoth model is

5:12

non-reasoning meaning that it may still

5:14

uh break down the task into a smaller

5:16

pieces but it's not really thinking or

5:18

um generating intermediate tokens. So

5:21

let's see how it responds to this.

5:27

Winning a touring um award is impressive

5:30

achievement that requires a deep

5:31

understanding. And then it started to

5:33

answer. It's actually giving me a plan

5:36

um which I don't think is possible. But

5:38

it's saying month one uh month one to

5:40

three month four to five four to six and

5:43

so on. And it it stopped here just

5:45

because I had a limit on the max tokens.

5:47

But basically as soon as I asked my

5:49

question it started to answer. So this

5:51

is the final um answer of this model.

5:54

Now let me use the exact same prompt and

5:56

switch to a reasoning model uh like

5:59

deepseek

6:03

and I'll keep the same max token uh

6:05

paste the exact same prompt and let's

6:07

see what happens now. Now it's this

6:10

reasoning here that appeared. If I click

6:13

on it, it's basically is showing all

6:14

those intermediate tokens that the model

6:16

is thinking.

6:18

So it's like, okay, the user just asked

6:20

how to win a touring award. First, the

6:22

user sounds excited about discovering AI

6:24

and looking deeper, they probably don't

6:27

actually care about the award itself.

6:29

But so um these are basically the

6:32

internal thinking of the model and then

6:34

right after this when it feels confident

6:35

to answer here, it started to produce

6:38

the final answer. And um it's basically

6:42

um just going on until uh it reaches the

6:45

max tokens.

6:47

So um this is what we refer to as the

6:50

reasoning models. These intermediate

6:52

tokens. Sometimes it's visible to the

6:54

user. In this case, DeepSc R1 is an open

6:56

model. So it's visible the exact

6:58

thinking process. Some other models like

7:00

OpenAI's reasoning models are not show

7:03

um showing the exact um reasoning

7:05

traces. It shows a rewrite of that or a

7:07

summary of that. Um but that's that's

7:10

about a concrete example

7:13

and these reasoning models are better

7:15

than non-reasoning LLMs. For example,

7:17

this is an screenshot from a leaderboard

7:20

and we see that the the highly ranked

7:22

LLMs are all reasoning LMS and the first

7:24

non-reasoning LLM is ranked fourth and

7:27

this screenshot is from a website called

7:29

El Marina. El Marina is basically a

7:32

public platform which evaluates

7:34

different LLMs by pairwise comparisons.

7:38

And here we are seeing that right now

7:40

the the top LLM is Gemini 2.5, GPT5 high

7:45

and cloud ops 4.1 and these are there is

7:47

a tie and there are other models and

7:50

still like top four top five models are

7:52

all reasoning alms. So this shows the

7:55

power and importance of reasoning alms

7:58

and in the rest of this video we will

8:00

learn different techniques to build

8:01

reasoning alms.

8:06

So there are lots of different

8:08

techniques that we can build a reasoning

8:10

model and these techniques can be

8:12

categorized into two big buckets.

8:14

Inference time techniques and training

8:17

time techniques.

8:19

Inference time techniques refers to

8:21

those that um keep the model unchanged.

8:23

So the parameters of the original LLM uh

8:26

is not touched and it's the same. So the

8:29

LLM itself is still non-reasoning. But

8:32

then we add a bunch of different modules

8:33

in different ways and different

8:35

algorithms to make this entire process

8:37

as look like as a reasoning process. So

8:40

generating intermediate tokens and then

8:42

the final answer and we will go over

8:44

different techniques. But basically the

8:46

LLM is not touched. It's the frozen LLM

8:52

training time techniques on the other

8:54

hand they use a training algorithm and

8:57

some data reasoning data typically to

9:00

continue fine-tuning this um

9:02

non-reasoning LLM and then the outcome

9:05

of this is going to be a reasoning LLM.

9:07

Now this reasoning LLM knows how to

9:09

reason internally. So when we want to

9:11

use it, we can just pass a prompt to it

9:13

and then um the output would look like a

9:15

reasoning output meaning that

9:17

intermediate tokens followed by an

9:19

answer. So in this case when we want to

9:22

use the model if it's reasoning LLM if

9:24

we use some training time technique to

9:26

build this reasoning LLM we no longer

9:28

need to add um additional modules.

9:32

So with that let's start with going

9:35

through different techniques for

9:36

inference time um reasoning models.

## Inference-time Techniques

9:44

All right, the first technique is

9:45

prompting and the idea of prompting is

9:48

to use prompt engineering to make LLM

9:50

generate intermediate tokens. Basically,

9:53

we are going from this setup which is um

9:55

a non-reasoning setup to it's this

9:58

additional module here called prompt

10:00

engineering and basically the prompt

10:03

first goes into here and then the output

10:05

of prompt engineering goes into the LL.

10:09

Let's see some examples.

10:11

For example, we can apply a few shot

10:14

chain of thought prompting. And what

10:16

that means is that let's say we have

10:17

this prompt. It's a math question. There

10:19

are three red bags with five apples and

10:22

so on. And then we pass it to this fshot

10:25

chain of thought prompting. And fshot

10:27

means that uh we show an example with

10:30

some intermediate tokens or with some um

10:32

reasoning traces and then we hope the

10:35

model to follow the same example. So

10:38

here what we see in red is the

10:39

additional thing that we are including

10:42

in as part of the prompt and basically

10:44

what we are having here is that answer 2

10:47

* 3= 6. So final answer is six

10:51

and then we have now solved this and

10:53

here this part is the original question.

10:57

Now when we pass this to the this

10:58

non-reasoning LLM this non-reasoning LLM

11:01

is understands this example and it tries

11:04

to follow that. So instead of outputting

11:07

the final answer, it's basically showing

11:09

all these intermediate steps and it's

11:11

trying to follow this exact uh structure

11:14

or template. For example, once it

11:16

reaches the final solution, it uses the

11:18

exact same uh format. So, comma, final

11:20

answer is six. So here it says so,

11:22

comma, final answer is 29.

11:25

So that's prompt engineering. And this

11:27

was few shot coot meaning that we show

11:29

one or some examples. We can also do

11:32

zero shot um coot. we just do uh we just

11:35

add let's think a step by step and just

11:38

adding this line allows the model to

11:40

also think and pushes the model to

11:43

actually think. So here we see that the

11:45

model tries to break down the task into

11:47

a smaller intermediate steps and solve

11:49

them

11:51

and there are more prompting techniques

11:52

but that's the highle overview of

11:54

prompting techniques to make a

11:56

non-reasoning LLM to reason.

12:00

The next technique is sequential

12:03

revision. And here basically the idea is

12:05

to refine the output of LLMs multiple

12:08

times using the same LLM. So instead of

12:11

passing the prompt to the LLM and

12:12

getting the output, we pass the prompt

12:15

to the LLM. Once the LLM provides the

12:17

output, we pass the output to the same

12:19

LLM again with some additional uh

12:22

instructions like evaluate this response

12:24

and improve it. And then we keep doing

12:26

this uh for a fixed number of

12:28

iterations.

12:30

And once it's over, we can pick the best

12:33

response or the final output.

12:36

This basically allows the model to

12:38

sequentially think and improve its

12:40

answers.

12:45

The next approach or technique is best

12:48

of n and the idea of best of n is very

12:52

simple. It is saying that we sample n

12:55

times from the llm in parallel and then

12:58

pick the best answer. So from this we go

13:01

to something like this. We for the same

13:04

prompt we sample n different times with

13:07

n different solutions basically and then

13:10

we have this additional component let's

13:11

call it selector and the selector looks

13:14

at all these responses for this prompt

13:16

and picks the best one and shows that to

13:18

the to the user and this becomes the

13:20

final output.

13:22

And for the selector there are different

13:24

ways we can build it. It can be just a

13:26

separate machine learning model called

13:28

reward model to look at all these u

13:31

responses and score them. It can be

13:33

simpler huristics like majority voting.

13:36

For example, in math questions, it can

13:38

look at different responses and pick um

13:40

whichever response that is more um

13:43

frequently appeared in all these sampled

13:45

responses or it can be any other uh

13:48

huristics.

13:51

Here is a short example for this prompt.

13:54

It's passed to the LLM. We also add this

13:57

let's think a step by step which we saw

13:58

earlier. And then this LLM we sample

14:01

three different solutions from it. And

14:03

we can see the first solution um has 29

14:07

as the final answer. The second one 28

14:09

and the last one 29. So the selector

14:12

here let's use let's assume we are using

14:14

majority voting would see that majority

14:16

of responses are believing the answer

14:18

the correct answer is 29. So it would

14:20

just pick one of those answers. And in

14:22

this case it's it's picking this one.

14:26

The last technique we would cover is

14:28

search against a verifier. And here

14:31

basically the idea is um instead of

14:33

having this setup we add a search

14:36

algorithm and then we rely on the LLM

14:38

and a a verifier to find the best

14:42

output. So I'll show some examples.

14:45

First let's see what is a verifier. A

14:47

verifier is simply a model trained to

14:49

score solutions or partial solutions. So

14:52

whenever we have some sequence of

14:54

thoughts, we can pass it to the verifier

14:57

and get some score and that score shows

14:59

that how good this response is for this

15:01

prompt. This is just a separate machine

15:03

learning model trained to do that and

15:06

the search algorithm relies on it to

15:08

explore different ideas or different

15:10

solutions

15:12

and search algorithm there are different

15:14

um just simply a search algorithm. It

15:16

can be a best of end which we saw

15:18

previously. It could be more advanced

15:20

searches like beam search, look ahead

15:22

search, Monte Carry search and so on.

15:26

So here is a a more concrete example

15:29

assuming that we have access to a

15:31

verifier. Best of end search algorithm

15:34

just generates n different u responses

15:37

and then all these responses goes into a

15:39

verifier. We get some score and then

15:42

best of end picks picks the best one.

15:45

Beam search is just making it more um

15:47

advanced and more efficient. So it's

15:50

passing these partial solutions to the

15:52

verifier to get the scores at each step

15:55

and then depending on the score it tries

15:57

it decides to prune or explore certain

15:59

branches more and we have look look

16:02

ahead search and there are more more

16:03

search uh algorithms.

16:06

So this is um search against verifier.

16:08

Before we go to training time techniques

16:11

let's see a summary of what we

16:13

discussed.

16:16

So a short summary is like this with

16:19

with um in a non-reasoning setup the

16:21

input we directly gets the output

16:25

in um prompting techniques like chain of

16:27

thought prompting which we saw from the

16:30

input we go to a sequence of thoughts

16:32

and then we get the final output

16:36

when it's combined with best of n we

16:38

basically sample multiple

16:41

um solutions in parallel And then here

16:44

depending on our selector it can be um

16:47

simply majority voting or some verifier

16:50

we can pick the best response and

16:53

use it as the final output. And in

16:55

search against a verifier we build this

16:58

um tree and we use the verifier to

17:01

explore more uh promising branches and

17:04

prune less promising branches until we

17:07

reach to a state where we feel

17:08

confident. And in this case this branch

17:10

is basically uh our final solution. Now

## Training-time Techniques

17:14

let's go to training time techniques.

17:20

So we already saw that the idea of

17:22

training time techniques is just to

17:24

continue training the base LLM to get a

17:26

reasoning LLM.

17:28

And there are two main ways to do this.

17:31

One is supervised finetuning. And here

17:34

basically just the idea is to fine-tune

17:36

this non-reasoning LLM on some chain of

17:38

thought data. And chain of thought data

17:41

is basically just a um uh pairs of

17:45

problem sequence of thoughts and the

17:47

final answer.

17:49

And if we train on this data this output

17:54

LLM this the outcome of this would be a

17:56

reasoning model.

17:58

And a popular example of this is a star

18:01

or selfreasoner.

18:03

And basically they're just explaining

18:04

how they use the base model to collect

18:07

coot data in this format question

18:10

rational answer. And then once we have

18:12

that they fine-tune LLM on this data to

18:15

get a better reasoning model. And

18:17

they're showing that they're just doing

18:19

it iteratively. So they keep

18:20

bootstrapping this model and getting

18:22

better and better coot data and

18:25

consequently getting better and better

18:27

reasoning alm. So if you're interested

18:29

you can take a look at this paper.

18:32

So this is supervised fine tuning. We

18:34

just basically continue training the

18:35

LLM.

18:38

The other technique is reinforcement

18:41

learning with a verifier. And basically

18:44

the idea here is to let the model let

18:46

this reasoning um LLM after SFTS stage

18:51

to practice. So the LLM can generate

18:54

multiple thoughts for the same prompt.

18:57

And then we have this verifier which

18:59

looks look looks at these responses and

19:01

score them. And then we apply we use a

19:03

reinforcement learning algorithm to look

19:05

at all these different responses and

19:08

update the parameters of the LLM such

19:10

that the LLM becomes more um encouraged

19:13

to

19:14

generate good answers and discouraged

19:18

from generating bad answers. Answers

19:21

which verifier believes that are not

19:23

good.

19:25

And a interesting paper showing that it

19:28

works really well is let's verify step

19:30

by step published by OpenAI. So if

19:32

you're interested to learn more about

19:34

this you can you can read this paper.

19:38

And for this verifier uh we have just

19:40

typically two two types of verifiers. It

19:43

can be either outcome supervised reward

19:44

model or OM which it scores the entire

19:48

solution. So it looks at all these

19:51

intermediate thoughts and the final

19:52

answer and score it or it can be process

19:55

supervised reward model where it scores

19:58

each individual thought separately. So

20:01

this is very detailed again if you're

20:03

interested you can go over this paper

20:04

but these are different types of

20:06

verifiers that we can in practice use.

20:10

The next technique is selfcorrection.

20:13

And the idea here is to train this LLM

20:16

on a data so that it learns to

20:18

selfcorrect itself.

20:21

So we go from here here to something

20:23

like this after training. So this LLM

20:27

now would generate some output then it

20:29

would self-correct it and it would self

20:30

correct it again.

20:34

And the key part of doing this is to

20:36

collect data. And again we can do

20:38

supervised finetuning or SFT. What we

20:41

need to do is to we need to collect

20:42

revision data which is basically a

20:44

sequence of incorrect answers followed

20:46

by the correct answer and then fine-tune

20:48

the LLM on this revision data.

20:51

Additionally we can also do

20:52

reinforcement learning for self

20:54

correction. And a popular example is a

20:57

score. I think it was published by

20:59

dimmine and it's just using

21:01

reinforcement algorithm to um to train

21:04

the model to selfcorrect itself.

21:08

So this is the third technique

21:10

selfcorrection.

21:12

The fourth technique which is the most

21:13

advanced one is to internalize search.

21:15

Basically collect some data and train

21:18

the LLM on this data so that the LLM

21:20

knows how to explore different

21:22

directions and reflect and backtrack and

21:25

and again um generate more solutions and

21:28

so on. So the key the key steps here is

21:31

just the data preparation. So we can use

21:34

um different techniques like inference

21:35

time techniques to sample different

21:37

solutions and then we can um once we

21:40

have the data we training is identical

21:43

to um SFT like identical to coot and

21:46

normal training and then after training

21:48

we would get this LLM that is able to

21:50

explore and reflect and backtrack.

21:53

Popular examples are meta coot or

21:55

journey learning and this is just

21:58

showing that after training a model to

22:00

uh on this uh kind of data the model is

22:03

able to generate some solutions and then

22:06

here it would backtrack and reflect and

22:08

generate more solutions and so on. So

22:11

this screenshot is from meta coot paper.

22:13

If you want to read in detail you can

22:15

you can go to this paper.

## GPT-5 Unified System

22:20

And finally uh we discussed all

22:22

different um inference time techniques

22:24

and training time techniques. Now let's

22:25

see what we know from GPT5.

22:29

So when the OpenAI released GPT5, they

22:32

also released this GPT5 system card and

22:35

it's a um very long article. It has uh

22:39

50 pages and they're sharing a lot of

22:41

information about it. But most of this

22:43

information is around evaluation and uh

22:46

safety mechanisms and how good the model

22:48

is. They're not sharing much about the

22:51

number of parameters or the architecture

22:53

that they've been using and so on. So

22:55

what I'm sharing here is what we know

22:58

from this system card and some other

23:00

reliable sources.

23:03

So we know a couple of things from GPD5.

23:05

One is that it GP5 unified system

23:08

consists of two models.

23:10

One is GPT5 main. It's named GPT5 main

23:14

and the other is GPT5 thinking.

23:17

GP GP5 main is more efficient so it's

23:21

less expensive but it's not a reasoning

23:23

model. GPT5 thinking is a reasoning

23:27

model and it can reason. So it's trained

23:30

for reasoning and how it's trained for

23:32

reasoning. It's not it's not um publicly

23:35

available. It's not known but it's very

23:37

likely that they're using one of the

23:39

techniques that we've already seen to

23:41

train this model to think. it's probably

23:44

having an SF uh SFDS stage uh

23:46

reinforcement learning with some

23:48

verifier and internalizing search.

23:51

So this is the first thing that we know.

23:54

The second thing we know about this is

23:56

that there is this fast uh fast router

23:59

that are put right before these models.

24:01

So whenever there is a prompt, the

24:02

prompt first goes to this router and

24:05

then the router decides which model to

24:07

use. For example, for certain prompts,

24:10

we do we do not need um thinking models.

24:13

The prompt is simply very simple. For

24:16

example, if we ask like where is a

24:17

capital of some u country for these kind

24:21

of questions, it's very likely that GPT5

24:23

main is sufficient and since it's less

24:25

likely less um expensive, so it's

24:27

preferred.

24:29

So the router decides where the prompt

24:32

should goes.

24:34

This is the second thing that it's

24:36

already explained in the system card.

24:40

And this router is very fast. it's um

24:42

it's not really costly.

24:46

The third thing we know from GPT5 is

24:49

that they're there's shifting their

24:51

focus from hard review results to safe

24:54

completions. So what that means is that

24:57

before GPT5 the models were using kind

25:01

of a intent classification on the input

25:03

prompt to decide whether it's a safe

25:06

prompt uh it's safe to answer this

25:08

prompt or no. So basically these models

25:10

were just using a binary classification

25:12

of user intent and then if they at that

25:15

stage if they believe that the input is

25:18

not safe it's not the user is not asking

25:20

a safe question they would just simply

25:23

refuse.

25:25

Whereas in GP5 they're switching the

25:28

focus on the output. So regardless of um

25:31

whether the input prompt is safe or not,

25:34

the GPT5 is optimized so that it can

25:36

produce answers that are safe.

25:40

And if you're interested, they have also

25:42

this um detailed paper about this safe

25:45

completions and this shift. So you can

25:47

just refer to this.

25:52

And finally they have also this thinking

25:55

pro mode in um GPD5.

26:00

So what that means is that um basically

26:03

in this mode they're just enabling test

26:05

time compute. So it's still the same

26:07

setup. It's still two models. There is

26:09

not any additional um pro model but the

26:13

difference is that now they are using

26:14

one of the inference time techniques

26:16

that we saw like uh self-consistency,

26:19

sequential revision, prompting and Monte

26:21

Carlo uh research and so on to explore

26:26

various uh solutions and various

26:28

directions to a prompt at the same time.

26:31

And then they are finally showing the

26:33

best one to the out to the user. So this

26:36

is what thinking pro mode means and just

26:39

to get a better sense if I go to chat

26:41

GPT here we have these modes instant is

26:46

basically um if we select instance it

26:49

means that we are asking the GPT5 to use

26:52

the non-reasoning model if we select

26:55

thinking it we are asking the model

26:57

regardless of whether our prompt is

26:59

simple or not to use the thinking model

27:02

and auto means that we rely on that

27:04

router to decide

27:06

and pro is simply we ask the model to

27:08

enable test time compute and use all

27:11

those uh inference time techniques that

27:12

we discussed.

27:15

All right, we can conclude the video. We

27:17

learned what reasoning LLMs are. We

27:20

explored various inference time and

27:22

training time techniques to build

27:23

reasoning LLMs and we also saw what GPT5

27:27

unified system might look like based on

27:29

their uh released system card.