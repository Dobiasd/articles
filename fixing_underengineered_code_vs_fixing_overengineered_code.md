# Fixing under-engineered code vs. fixing over-engineered code

![(puzzle)](fixing_underengineered_code_vs_fixing_overengineered_code/puzzle.jpg)

Recently I was playing around with the following question:

> **Is it easier to fix underengineering in a codebase or overengineering?**

This question naively assumes that there is a "right" level of engineering, which, in reality, of course, depends on the requirements, expected future of the project, company culture, etc. But let's pretend there is such an ideal level.

Let's also pretend we all have some similar understanding of what both terms mean.

**Underengineering might have the following ingredients:**
- too few abstractions
- entangled concerns (non-SOLID code)
- spaghetti

**Overengineering might consist of the following:**
- too many abstractions
- consequently, very deep call stacks
- violating the YAGNI principle

While talking to people about this, I heard different opinions, many of them, naturally, including an "it depends", but I found the analogy my colleague Benjamin (CPO, former CTO, former ingenious software developer) spontaneously came up with especially striking, so I'd like to present it here. :slightly_smiling_face:

**Fixing underengineering is like solving a jigsaw puzzle.** It's easy in the small, but the complexity grows exponentially with the number of pieces.

![(puzzle_underengineering)](fixing_underengineered_code_vs_fixing_overengineered_code/puzzle_underengineering.jpg)

**Fixing overengineering is removing superfluous abstractions.** It scales linearly with the size.

![(puzzle_overengineering)](fixing_underengineered_code_vs_fixing_overengineered_code/puzzle_overengineering.jpg)

Thus, for small projects, underengineering might be easier to fix, but once the project grows in size, overengineering is less troublesome to remove afterwards. Of course, the initial cost to develop the overengineered solution might be somewhat higher, but that's not the point of this article. :wink:
