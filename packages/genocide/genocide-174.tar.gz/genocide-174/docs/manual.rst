.. _manual:

.. raw:: html

    <br><br>

.. title:: Manual


**NAME**

    **GENOCIDE** - Elderly, Handicapped, Criminals, Wicked `! <source.html>`_


**SYNOPSIS**

    ::

        genocide  <cmd> [key=val] [key==val]
        genocidec [-i] [-v]
        genocided 


**DESCRIPTION**

    ``GENOCIDE`` holds evidence that king
    netherlands is doing a genocide, a
    written response where king
    netherlands confirmed taking note
    of “what i have written”, namely
    :ref:`proof  <evidence>` that medicine
    he uses in treatement laws like zyprexa,
    haldol, abilify and clozapine are
    poison that make impotent, is both
    physical (contracted muscles) and
    mental (make people hallucinate)
    torture and kills members of the
    victim groups.

    ``GENOCIDE`` contains :ref:`correspondence
    <writings>` with the International Criminal
    Court, asking for arrest of the king of the
    netherlands, for the genocide he is committing
    with his new treatement laws.

    Current status is a :ref:`"no basis to proceed"
    <writings>` judgement of the prosecutor which
    requires a :ref:`"basis to prosecute" <home>`
    to have the king actually arrested.


**INSTALL**

    ::

        $ pipx install genocide
        $ pipx ensurepath

        $ genocide srv > genocide.service
        # mv *.service /etc/systemd/system/
        # systemctl enable genocide --now

        joins #genocide on localhost


**USAGE**

    without any argument the bot does nothing

    ::

        $ genocide
        $

    see list of commands

    ::

        $ genocide cmd
        cmd,req,skl,srv


    start a console

    ::

        $ genocidec
        >

    start daemon

    ::

        $ genocided
        $ 


    show request to the prosecutor

    ::

        $ genocide req
        Information and Evidence Unit
        Office of the Prosecutor
        Post Office Box 19519
        2500 CM The Hague
        The Netherlands


**CONFIGURATION**

    irc

    ::

        $ genocide cfg server=<server>
        $ genocide cfg channel=<channel>
        $ genocide cfg nick=<nick>

    sasl

    ::

        $  genocide pwd <nsvnick> <nspass>
        $  genocide cfg password=<frompwd>

    rss

    ::

        $  genocide rss <url>
        $  genocide dpl <url> <item1,item2>
        $  genocide rem <url>
        $  genocide nme <url> <name>


**COMMANDS**

    ::

        cfg - irc configuration
        cmd - commands
        mre - displays cached output
        pwd - sasl nickserv name/pass
        req - reconsider


**SOURCE**


    source is :ref:`here <source>`


**FILES**

    ::

        ~/.genocide 
        ~/.local/bin/genocide
        ~/.local/bin/genocidec
        ~/.local/bin/genocided
        ~/.local/pipx/venvs/genocide/*


**AUTHOR**

    Bart Thate <bthate@dds.nl>


**COPYRIGHT**

    ``GENOCIDE`` is Public Domain.
