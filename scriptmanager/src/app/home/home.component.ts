import { Component, OnInit } from '@angular/core';
import { FossService } from '../_service/foss.service';
import { TutorialsService } from '../_service/tutorials.service'
import { AuthService } from '../_service/auth.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.sass']
})
export class HomeComponent implements OnInit {

  public fossCategories;
  public currentCategoryLanguages;
  public tutorials;
  public description: string = '';
  
  constructor(
    public fossService: FossService,
    public tutorialService: TutorialsService,
    public authService: AuthService
  ) { }

  private getFossCategoryIndex() {
    const fossId = +this.fossService.currentFossCategory;
    
    for (var i = 0; i < this.fossCategories.length; i++) {
      const fid = this.fossCategories[i]['foss_category']['id'];

      if (fid === fossId) return i;
    }

    return -1;
  }

  private getFossCategoryLanguageIndex() {
    const languageId = +this.fossService.currentFossCategoryLanguage;
    
    for (var i = 0; i < this.currentCategoryLanguages.length; i++) {
      const lid = this.currentCategoryLanguages[i]['id'];

      if (lid === languageId) return i;
    }

    return -1;
  }

  public onFossCategoryChange(fid) {
    this.fossService.currentFossCategory = fid;
    const index = this.getFossCategoryIndex();

    this.tutorials = [];
    this.fossService.currentFossCategoryLanguage = -1;
    this.description = '';
    this.currentCategoryLanguages = [];

    if (index !== -1) {
      this.description = this.fossCategories[index]['foss_category']['description'];
      this.currentCategoryLanguages = this.fossCategories[index]['languages'];
    }

  }

  public onLanguageChange(lid) {
    this.fossService.currentFossCategoryLanguage = lid;
    const index = this.getFossCategoryLanguageIndex();

    if (index !== -1) {
      const fossId = this.fossService.currentFossCategory;
      const languageId = this.fossService.currentFossCategoryLanguage;
      
      this.fetchTutorials(fossId, languageId);
    } else {
      this.tutorials = [];
      this.description = '';
    }
  }

  public fetchAllFoss() {
    this.fossService.getAllFossCategories().subscribe(
      (res) => {
        this.fossCategories = res['data'];

        const fossId = this.fossService.currentFossCategory;
        const languageId = this.fossService.currentFossCategoryLanguage;
    
        if (fossId !== -1 && languageId !== -1) {
          this.onFossCategoryChange(fossId);
          this.onLanguageChange(languageId);
        }
      },
      (err) => {
        console.log('Failed to fetch foss categories');
        console.error(err);
      }
    );
  }

  public fetchTutorials(fossId, languageId) {
    this.tutorialService.getFossTutorials(fossId, languageId).subscribe(
      (res) => this.tutorials = res,
      console.error
    );
  }

  ngOnInit() {
    this.fetchAllFoss();
  };

}
