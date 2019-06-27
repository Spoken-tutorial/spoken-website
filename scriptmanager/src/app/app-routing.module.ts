import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { ScriptCreateComponent } from './script/script-create/script-create.component';
import { ScriptEditComponent } from './script/script-edit/script-edit.component';
import { ScriptViewComponent } from './script/script-view/script-view.component';
import { ScriptRevisionComponent } from './script/script-revision/script-revision.component';
import {ScriptUploadComponent } from './script/script-upload/script-upload.component'
const routes: Routes = [
  {
    path: '',
    component: HomeComponent,
    data: {
      title: 'List of Tutorials',
      animation: 'HomePage'
    }
  },
  {
    path: 'create/:id/:tutorialName',
    component: ScriptCreateComponent,
    data: {
      title: 'Create Script',
      animation: 'HomePage'
    }
  },
  {
    path: 'upload/:id/:tutorialName',
    component: ScriptUploadComponent,
    data: {
      title: 'Upload Script',
      animation: 'HomePage'
    }
  },

  {
    path: 'edit/:id/:tutorialName',
    component: ScriptEditComponent,
    data: {
      title: 'Edit Script',
      animation: 'HomePage'
    }
  },
  {
    path: 'view/:id/:tutorialName',
    component: ScriptViewComponent,
    data: {
      title: 'Edit Script',
      animation: 'HomePage'
    }
  },
  {
    path: 'revisions',
    component: ScriptRevisionComponent,
    data: {
      title: 'Revisions',
      animation: 'HomePage'
    }
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
