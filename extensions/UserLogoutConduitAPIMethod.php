<?php

final class UserLogoutConduitAPIMethod extends UserConduitAPIMethod {

  public function getAPIMethodName() {
    return 'user.logout';
  }

  public function getMethodDescription() {
    return pht('Logout specified users (admin only).');
  }

  protected function defineParamTypes() {
    return array(
      'phids' => 'required list<phid>',
    );
  }

  protected function defineReturnType() {
    return 'void';
  }

  protected function defineErrorTypes() {
    return array(
      'ERR-PERMISSIONS' => pht('Only admins can call this method.'),
      'ERR-BAD-PHID' => pht('Non existent user PHID.'),
    );
  }

  protected function execute(ConduitAPIRequest $request) {
    $actor = $request->getUser();
    if (!$actor->getIsAdmin()) {
      throw new ConduitException('ERR-PERMISSIONS');
    }

    $phids = $request->getValue('phids');

    $users = id(new PhabricatorUser())->loadAllWhere(
      'phid IN (%Ls)',
      $phids);

    if (count($phids) != count($users)) {
      throw new ConduitException('ERR-BAD-PHID');
    }

    $engine = id(new PhabricatorAuthSessionEngine());
    foreach ($users as $user) {
      $engine->terminateLoginSessions($user);
    }
  }

}

