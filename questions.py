QUESTIONS = [
    'Вам грустно или вы в плохом настроении?',
    'Чувствуете грусть, удручены?',
    'Чувствуете желание расплакаться, слезливость?',
    'Чувствуете уныние?',
    'Испытываете чувство безнадежности?',
    'Имеете низкую самооценку?',
    'Испытываете чувство собственной ничтожности и непригодности?',
    'Испытываете чувство вины или стыда?',
    'Критикуете или обвиняете самого себя?',
    'Испытываете трудности с принятием решений?',

    'Чувствуете потерю интереса к членам семьи, друзьям, коллегам?',
    'Испытываете одиночество?',
    'Проводите меньше времени с семьей или с друзьями?',
    'Чувствуете потерю мотивации?',
    'Чувствуете потерю интереса к работе или другим занятиям?',
    'Избегаете работы и другой деятельности?',
    'Ощущаете потерю удовольствия и нехватку удовлетворения от жизни?',

    'Чувствуете усталость?',
    'Испытываете затруднения со сном или, наоборот, слишком много спите?',
    'Имеете сниженный или, наоборот, повышенный аппетит?',
    'Замечаете потерю интереса к сексу?',
    'Беспокоитесь по поводу своего здоровья?',

    'Имеются ли у вас суицидальные мысли?',
    'Хотели бы вы окончить свою жизнь?',
    'Планируете ли вы навредить себе?'
]


def get_paragraph(question_number):
    if 0 <= question_number <= 9:
        return 'Мысли и чувства'
    if 10 <= question_number <= 16:
        return 'Деятельность и личные отношения'
    if 17 <= question_number <= 21:
        return 'Физические симптомы'
    if 22 <= question_number <= 24:
        return 'Суицидальные побуждения'
