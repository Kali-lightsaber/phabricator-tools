/**
 * Copyright 2018
 * MIT License
 * Phabricator specific handling
 */
module projects;
import common;
import phabricator.api;
import phabricator.common;
import std.string: join;
import std.stdio: writeln;

/**
 * Join projects
 */
private static void doJoinProjects(API api)
{
    try
    {
        auto settings = getSettings(api);
        auto user = api.context[PhabricatorUser];
        auto proj = construct!ProjectAPI(settings);
        auto membership = proj.membersActive()[ResultKey][DataKey];
        string[] results;
        foreach (project; membership.array)
        {
            auto members = project["attachments"]["members"]["members"].array;
            auto matched = false;
            foreach (member; members)
            {
                auto phid = member["phid"].str;
                if (phid == user)
                {
                    matched = true;
                    break;
                }
            }

            if (!matched)
            {
                results ~= project[FieldsKey]["name"].str;
            }
        }

        if (results.length > 0)
        {
            auto assigned = assignToActive(getSettings(api), user);
            writeln("not a member of these projects:\n" ~ join(results, "\n"));
            if (!assigned)
            {
                writeln("unable to assign self to projects...");
            }
        }
    }
    catch (Exception e)
    {
        writeln("unexepected exception joining projects");
        writeln(e);
    }
}

/**
 * Entry point
 */
void main(string[] args)
{
    auto api = setup(args);
    doJoinProjects(api);
    info("projects");
}

/**
 * Assign a user to all active projects
 */
private static bool assignToActive(Settings settings, string userPHID)
{
    try
    {
        auto proj = construct!ProjectAPI(settings);
        auto actives = proj.active()[ResultKey][DataKey].array;
        foreach (active; actives)
        {
            try
            {
                proj.addMember(active["phid"].str, userPHID);
            }
            catch (PhabricatorAPIException e)
            {
                // Ignore phabricator API exceptions
            }
        }

        return true;
    }
    catch (Exception e)
    {
        writeln(e);
        return false;
    }
}
